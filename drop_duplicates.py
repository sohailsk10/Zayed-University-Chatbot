# import pandas as pd

# temp = []
# df = pd.read_csv("Main_df.csv")
# path = df['path']
# temp.append(path)

# print(temp)
# for i in temp:
#     var = set(i)
#     print(var)

# df = df.drop_duplicates(subset="path",keep=False, inplace=True)

# print(df)

def modify_url(url_list):
    modified_urls = []
    for url in url_list:
        if 'https://www.zu.ac.ae' in url:
            modified_urls.append(url + '.aspx')
        elif 'https://eservices.zu.ac.ae' in url:
            modified_urls.append(url)
    return modified_urls

urls = ['https://eservices.zu.ac.ae/Service/en/Card/Issue-a-Student-ID-Card-as-a-replacement--Dubai-Campus-Only--',
        'https://www.zu.ac.ae/main/en/student_orientation/_outdated/index',
        'https://eservices.zu.ac.ae/Service/en/Card/Master-Programs---To-Whom-It-May-Concern-Letter---Digital-PDF',
        'https://www.zu.ac.ae/main/en/admission/undergraduate-programs/admission-requirement/_uae-nationals/transfer-diploma-students']

modified_urls = modify_url(urls)
print(modified_urls)


        