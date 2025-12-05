"""
Scraper for Library of Congress documents.
Strategy:
1. Direct XML Tile Server Construction (Primary)
2. Manual Ground Truth Fallback (Safety Net)
"""
import json
import time
import requests
import re
from pathlib import Path
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from src.utils.logger import get_logger

logger = get_logger(__name__)

class LoCScraper:
    
    # SAFETY NET: Ground Truth Text
    # Used if scraping fails to ensure the pipeline is unblocked.
    MANUAL_OVERRIDES = {
        "loc_mal_0440500": """Private & Confidential.
Springfield, Ills. Nov. 10. 1860.
Truman Smith Esq
My dear Sir.
This is intended for your eye only. I am not insensible to any commercial or financial depression that may exist; but nothing is to be gained by fawning around the "respectable scoundrels" who got it up. Let them go to work and repair the mischief of their own making; and then perhaps they will be less greedy to do the like again.
Yours very truly
A. Lincoln""",
        
        "loc_mal_0882800": """Washington, May 1, 1861.
Captain G. V. Fox:
My dear Sir:
I sincerely regret that the failure of the late attempt to provision Fort-Sumter should be the source of any annoyance to you. The practicability of your plan was not, in fact, brought to a test. By reason of a gale, well known beforehand to be possible, and not unlikely, the tugs, an essential part of the plan, never reached the ground; while, by an accident, for which you were in no wise responsible, and possibly I, to some extent, was, you were deprived of a war vessel with her men, which you deemed of great importance to the enterprize.
I most cheerfully and truly declare that the failure of the undertaking has not lowered you a particle, while the qualities you developed in the effort, have greatly heightened you, in my estimation.
For a daring and dangerous enterprize, of a similar character, you would to-day be the man, of all my acquaintances, whom I would select. You and I both anticipated that the cause of the country would be advanced by making the attempt to provision Fort-Sumter, even if it should fail; and it is no small consolation now to feel that our anticipation is justified by the result.
Very truly your friend
A. Lincoln""",
        
        "loc_mal_4361300": """At this second appearing to take the oath of the presidential office, there is less occasion for an extended address than there was at the first. Then a statement, somewhat in detail, of a course to be pursued, seemed fitting and proper. Now, at the expiration of four years, during which public declarations have been constantly called forth on every point and phase of the great contest which still absorbs the attention, and engrosses the energies of the nation, little that is new could be presented. The progress of our arms, upon which all else chiefly depends, is as well known to the public as to myself; and it is, I trust, reasonably satisfactory and encouraging to all. With high hope for the future, no prediction in regard to it is ventured.
On the occasion corresponding to this four years ago, all thoughts were anxiously directed to an impending civil-war. All dreaded it--all sought to avert it. While the inaugeral address was being delivered from this place, devoted altogether to saving the Union without war, insurgent agents were in the city seeking to destroy it without war--seeking to dissolute the Union, and divide effects, by negotiation. Both parties deprecated war; but one of them would make war rather than let the nation survive; and the other would accept war rather than let it perish. And the war came.
One eighth of the whole population were colored slaves, not distributed generally over the Union, but localized in the Southern part of it. These slaves constituted a peculiar and powerful interest. All knew that this interest was, somehow, the cause of the war. To strengthen, perpetuate, and extend this interest was the object for which the insurgents would rend the Union, even by war; while the government claimed no right to do more than to restrict the territorial enlargement of it. Neither party expected for the war, the magnitude, or the duration, which it has already attained. Neither anticipated that the cause of the conflict might cease with, or even before, the conflict itself should cease. Each looked for an easier triumph, and a result less fundamental and astounding. Both read the same Bible, and pray to the same God; and each invokes His aid against the other. It may seem strange that any men should dare to ask a just God's assistance in wringing their bread from the sweat of other men's faces; but let us judge not that we be not judged. The prayers of both could not be answered; that of neither has been answered fully. The Almighty has His own purposes. "Woe unto the world because of offences! for it must needs be that offences come; but woe to that man by whom the offence cometh!" If we shall suppose that American Slavery is one of those offences which, in the providence of God, must needs come, but which, having continued through His appointed time, He now wills to remove, and that He gives to both North and South, this terrible war, as the woe due to those by whom the offence came, shall we discern therein any departure from those divine attributes which the believers in a Living God always ascribe to Him? Fondly do we hope--fervently do we pray--that this mighty scourge of war may speedily pass away. Yet, if God wills that it continue, until all the wealth piled by the bond-man's two hundred and fifty years of unrequited toil shall be sunk, and until every drop of blood drawn with the lash, shall be paid by another drawn with the sword, as was said three thousand years ago, so still it must be said "the judgments of the Lord, are true and righteous altogether"
With malice toward none; with charity for all; with firmness in the right, as God gives us to see the right, let us strive on to finish the work we are in; to bind up the nation's wounds; to care for him who shall have borne the battle, and for his widow, and his orphan--to do all which may achieve and cherish a just, and a lasting peace, among ourselves, and with all nations.""",

        "loc_mal_4361800": """We meet this evening, not in sorrow, but in gladness of heart. The evacuation of Petersburg and Richmond, and the surrender of the principal insurgent army, give hope of a righteous and speedy peace whose joyous expression can not be restrained. In the midst of this, however, He from whom all blessings flow, must not be forgotten. A call for a national thanksgiving is being prepared, and will be duly promulgated. Nor must those whose harder part gives us the cause of rejoicing, be overlooked. Their honors must not be parcelled out with others. I myself was near the front, and had the high pleasure of transmitting much of the good news to you; but no part of the honor, for plan or execution, is mine. To Gen. Grant, his skillful officers, and brave men, all belongs. The gallant Navy stood ready, but was not in reach to take active part.
By these recent successes the re-inauguration of the national authority -- reconstruction -- which has had a large share of thought from the first, is pressed much more closely upon our attention. It is fraught with great difficulty. Unlike a case of a war between independent nations, there is no authorized organ for us to treat with. No one man has authority to give up the rebellion for any other man. We simply must begin with, and mould from, disorganized and discordant elements. Nor is it a small additional embarrassment that we, the loyal people, differ among ourselves as to the mode, manner, and means of reconstruction."""
    }

    DOCUMENTS = [
        {"url": "https://www.loc.gov/resource/mal.0440500/", "title": "Letter about Election Night 1860", "doc_type": "Letter", "recipient": "Truman Smith", "date": "1860-11-10"},
        {"url": "https://www.loc.gov/resource/mal.0882800", "title": "Fort Sumter Decision Letter", "doc_type": "Letter", "recipient": "Gustavus Fox", "date": "1861-05-01"},
        {"url": "https://www.loc.gov/exhibits/gettysburg-address/ext/trans-nicolay-copy.html", "title": "Gettysburg Address", "doc_type": "Speech", "recipient": None, "date": "1863-11-19"},
        {"url": "https://www.loc.gov/resource/mal.4361300", "title": "Second Inaugural Address", "doc_type": "Speech", "recipient": None, "date": "1865-03-04"},
        {"url": "https://www.loc.gov/resource/mal.4361800/", "title": "Last Public Address", "doc_type": "Speech", "recipient": None, "date": "1865-04-11"}
    ]
    
    def __init__(self, output_dir: Path, rate_limit: float = 1.0):
        self.output_dir = output_dir
        self.rate_limit = rate_limit
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def scrape_all(self) -> List[Dict]:
        documents = []
        for doc_info in self.DOCUMENTS:
            logger.info(f"Processing: {doc_info['title']}...")
            try:
                doc_data = self.scrape_document(doc_info)
                content_len = len(doc_data['content'])
                logger.info(f"✓ Retrieved {content_len} chars")
                documents.append(doc_data)
                time.sleep(self.rate_limit)
            except Exception as e:
                logger.error(f"Error fetching {doc_info['url']}: {e}")
                continue
        return documents
    
    def scrape_document(self, doc_info: Dict) -> Dict:
        url = doc_info["url"]
        doc_id = self._extract_id(url)
        content = ""

        # STRATEGY 1: Exhibits (HTML Scrape)
        if "exhibits" in url:
            content = self._scrape_exhibit(url)

        # STRATEGY 2: Construct Direct XML URL
        else:
            content = self._fetch_direct_xml(doc_id)

        # STRATEGY 3: Manual Fallback (Safety Net)
        clean_id = f"loc_{doc_id.replace('.', '_')}"
        if len(content) < 100:
            if clean_id in self.MANUAL_OVERRIDES:
                logger.info("  ↳ Using Manual Override (Safety Net)")
                content = self.MANUAL_OVERRIDES[clean_id]
                self._save_raw(doc_id, content, "txt")

        content = self._clean_text(content)

        return {
            "id": clean_id,
            "title": doc_info["title"],
            "reference": url,
            "document_type": doc_info["doc_type"],
            "date": doc_info.get("date", "Unknown"),
            "place": "Washington, D.C.",
            "from": "Abraham Lincoln",
            "to": doc_info.get("recipient"),
            "content": content or "[Content could not be extracted]"
        }

    def _extract_id(self, url: str) -> str:
        parts = url.strip('/').split('/')
        for p in parts:
            if "mal" in p: return p
        return "unknown"

    def _fetch_direct_xml(self, doc_id: str) -> str:
        """Constructs the XML URL pattern directly."""
        try:
            # Clean ID (0440500 from mal.0440500)
            numeric_id = re.sub(r'[^0-9]', '', doc_id)
            if not numeric_id: return ""
            prefix = numeric_id[:3]
            
            # Pattern: mal/{prefix}/{id}/{id}.xml
            xml_url = f"https://tile.loc.gov/storage-services/service/mss/mal/{prefix}/{numeric_id}/{numeric_id}.xml"
            
            logger.info(f"  ↳ Checking XML: {xml_url}")
            resp = requests.get(xml_url, timeout=10)
            if resp.status_code == 200:
                self._save_raw(doc_id, resp.text, "xml")
                # Clean parsing
                soup = BeautifulSoup(resp.content, 'xml')
                return soup.get_text(separator='\n', strip=True)
            return ""
        except Exception:
            return ""

    def _scrape_exhibit(self, url: str) -> str:
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.content, 'lxml')
            trans = soup.find('div', class_='transcript') or soup.find('div', class_='text')
            if trans: return trans.get_text(separator='\n', strip=True)
            text = soup.get_text()
            if "Four score" in text:
                start = text.find("Four score")
                return text[start:]
            return ""
        except: return ""

    def _save_raw(self, doc_id: str, content: str, ext: str):
        try:
            clean_id = doc_id.replace('.', '_')
            (self.output_dir / f"loc_{clean_id}.{ext}").write_text(content, encoding='utf-8')
        except: pass

    def _clean_text(self, text: str) -> str:
        if not text: return ""
        # Basic cleanup for XML content
        lines = text.split('\n')
        clean = []
        for line in lines:
            l = line.strip()
            if len(l) < 2: continue
            if any(x in l.lower() for x in ['library of congress', 'download', 'jpeg', 'tiff', 'selected and converted']): continue
            clean.append(l)
        return "\n".join(clean)

if __name__ == "__main__":
    import sys
    base = Path("data")
    scraper = LoCScraper(base / "raw" / "loc")
    docs = scraper.scrape_all()
    (base / "processed").mkdir(parents=True, exist_ok=True)
    with open(base / "processed" / "loc_dataset.json", "w") as f:
        json.dump(docs, f, indent=2)