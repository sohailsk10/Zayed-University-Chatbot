from sklearn.metrics.pairwise import cosine_similarity


def cosine_similarity_fn(new_df, questions_asked_vec, questions_vec):
    score = []
    dump_score = []
    print("INDSIDE CS")
    # for i in range(len(questions)):
    # new_df['question'] = new_df[['title', 'description']].apply(lambda x: ''.join(x), axis=1)
    for i in range(len(new_df['title'])):
    # for i in range(len(new_df['path'])):
        cs = cosine_similarity([questions_asked_vec][0], [questions_vec[i]])
        # qtag_value = questions.get('qtag')[i]
        qtag_value = new_df['q_tag'][i]
        current_score = (qtag_value, cs[0][0])
        if len(dump_score) == 0:
            dump_score.append(current_score)
        else:
            for j in range(len(dump_score)):
                if dump_score[j][1] < current_score[1]:
                    dump_score.insert(j, current_score)
                    dump_score.pop(j + 1)
        # print("cs[0][0]", cs[0][0])

        if cs[0][0] > 0.65:
            if len(score) == 0:
                score.append(current_score)
            else:
                prev_len = len(score)
                j = 0
                while j < len(score):
                    if current_score not in score:
                        if score[j][1] < current_score[1] and score[j][0] != current_score[0]:
                            score.insert(j, current_score)
                        elif score[j][1] < current_score[1] and score[j][0] == current_score[0]:
                            score.insert(j, current_score)
                            score.pop(j + 1)
                            break
                        elif score[j][1] >= current_score[1] and score[j][0] == current_score[0]:
                            j += 1
                            continue
                        elif j == len(score) - 1:
                            score.append(current_score)
                            break
                    else:
                        if score[j][1] < current_score[1] and score[j][0] == current_score[0]:
                            score.pop(j)
                    j += 1
    if len(score) == 0:
        if len(dump_score) == 0:
            return "Sorry, I don't know the answer to that question."
        else:
            score = dump_score

    print("score", score)
    

    ans_disp = ""
    ans_list = []
    tags = []
    for index, value in score:
        tag = new_df['path'][index]
        if tag not in tags:
            tags.append(tag)
        ans_disp += list(new_df.loc[new_df['path'] == tag]['path'])[0] + "\n"
        ans_list.append(list(new_df.loc[new_df['path'] == tag]['path'])[0])
    
    score_sum = 0
    
    for j in range(len(score)):
        if j < 5:
            score_sum+=score[j][1]
            
    if len(score) <= 5:
        score_avg = score_sum/len(score)
    else:
        score_avg = score_sum/5

    return ans_disp, ans_list, score_avg
