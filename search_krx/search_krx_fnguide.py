import requests
from bs4 import BeautifulSoup

def fetch_financial_highlight(stock_code):
	url = f"https://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A{stock_code}&cID=&MenuYn=Y&ReportGB=&NewMenuID=11&stkGb=701"
	headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
	}
	res = requests.get(url, headers=headers)
	res.raise_for_status()
	soup = BeautifulSoup(res.text, "html.parser")
	highlight_div = soup.find("div", id="highlight_D_A")
	if not highlight_div:
		return None
	table = highlight_div.find("table")
	if not table:
		return None
	rows = table.find_all("tr")
	data = {}
	# 연도 정보 추출 (display:none; 속성 무시, 실제로 보이는 텍스트만 4개 추출)
	years = []
	thead = table.find("thead")
	if thead:
		ths = thead.find_all("th")
		for th in ths:
			for elem in th.find_all(string=True):
				parent = elem.parent
				# 상위에 display:none이 있으면 무시
				ignore = False
				while parent is not None and parent != th:
					if parent.get('style') and 'display:none' in parent.get('style'):
						ignore = True
						break
					parent = parent.parent
				if ignore:
					continue
				text = elem.strip()
				# 연도 형식(예: 2023/12, 2024/12(E) 등)만 추출
				if text and ('/' in text and text[:4].isdigit()):
					if text not in years:
						years.append(text)
						if len(years) == 4:
							break
	# 주요 지표 추출 (EPS, BPS는 '지배주주'가 포함된 행 우선)
	indicators = ["ROA", "ROE", "EPS", "BPS", "DPS", "PER", "PBR", "배당수익률"]
	indicator_rows = {ind: [] for ind in indicators}
	for row in rows:
		cells = row.find_all(["th", "td"])
		if not cells:
			continue
		name = cells[0].get_text(strip=True)
		for indicator in indicators:
			if indicator in name:
				indicator_rows[indicator].append((name, cells))
	# 실제 데이터 추출
	for indicator in indicators:
		rows_list = indicator_rows[indicator]
		selected = None
		if indicator in ["EPS", "BPS"]:
			# '지배주주'가 포함된 행 우선
			for name, cells in rows_list:
				if "지배주주" in name:
					selected = cells
					break
			if not selected and rows_list:
				selected = rows_list[0][1]
		else:
			if rows_list:
				selected = rows_list[0][1]
		if selected:
			values = []
			for td in selected[1:]:
				val = td.get_text(strip=True).replace(",", "")
				if val.replace("-", "").replace(".", "").isdigit() or val == "-":
					values.append(val)
			data[indicator] = values[:4]
	return {"years": years[:4], "data": data}

def fetch_multiple_stocks(stock_codes_dict):
	result = {}
	for code in stock_codes_dict:
		data = fetch_financial_highlight(code)
		result[code] = data
	return result

def print_tsv(stock_codes_dict):
	indicators = ["ROA", "ROE", "PER", "PBR", "배당수익률", "EPS", "DPS", "BPS"]
	result = fetch_multiple_stocks(stock_codes_dict)
	for code, name in stock_codes_dict.items():
		item = result.get(code)
		if not item:
			continue
		years = item["years"]
		data = item["data"]
		if not years:
			continue
		# 헤더: 종목코드\t종목명\t지표\t연도1\t연도2 ...
		header = ["종목코드", "종목명", "지표"] + years
		print("\t".join(header))
		for ind in indicators:
			row = [code, name, ind]
			val_list = data.get(ind, [])
			for i in range(len(years)):
				row.append(val_list[i] if i < len(val_list) else "")
			print("\t".join(row))

if __name__ == "__main__":
	stock_codes = {
		"086790": "하나금융지주",
		"005380": "현대차",
		"316140": "우리금융지주",
		"000810": "삼성화재",
		"000270": "기아",
		"005830": "DB손해보험"
	}
	print_tsv(stock_codes)
