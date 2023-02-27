from pre_process_ds import pre_process
import pandas as pd
from utils import get_proper_link


# message1 = "pull out promanade competition pdf"
# message1 = "pull out alumni cv checklist"
# message1 = "Pull out the list of about the sasd services"
# message1 = "get me college of interdisciplinary faculty and staff"
# message1 = "I am looking for Convention Cener fact sheet in pdf"
message1 = "about the zu"
# message1 = "how to apply for student car registration"
# message1 = "Where can I get the service to issue a Student ID Card as a replacement (Dubai Campus Only)"
# message1 = "I am looking for Convention Cener Brochure in English pdf"
# message1 = "Pull out the list of about the library services"
# message1 = "Pull out the list of about the ice services"
# message1 = "Pull out the list of about the eservices"

data = pd.read_csv("CSV\\MAIN3.csv")
links = data.path.values.tolist()
ids = data.id.values.tolist()

processed_message = pre_process(message1).split()

question_length = len(processed_message)
processed_message_set = set(processed_message)

print(processed_message)

jaccard = {}

for i in range(len(links)):
    if "/ar/" not in links[i]:
        process_link = set(pre_process(get_proper_link(links[i])).split())
        jaccard[ids[i]] = ([len(processed_message_set.intersection(process_link)) / len(processed_message_set.union(process_link))])

sorted_dict = {k: v for k, v in sorted(jaccard.items(), key=lambda item: item[1], reverse=True)[:10]}
print(sorted_dict)

for key, _ in sorted_dict.items():
    print(links[ids.index(key)])