links = ['https://www.zu.ac.ae/main/en/CAFO-units/_unused/Convention-Centers', 'https://www.zu.ac.ae/main/en/ZUCC/index',
         'https://www.zu.ac.ae/main/files/contents/open_data/zu_fact_sheet.pdf','https://www.zu.ac.ae/main/en/ZUCC_AUH/index',
         'https://www.zu.ac.ae/main/en/e-participation/e-participation-policy.aspx','https://www.zu.ac.ae/main/en/fall-2022-programs/index.aspx']

index_links = [link for link in links if 'index' in link]
other_links = [link for link in links if 'index' not in link]

result = index_links + other_links

print(result)