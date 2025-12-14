import re
import simple_pickle as sp
def split_text(text,max_len=512):
    # 准备块容器
    paras = []
    if len(text) <= max_len:
        paras.append(text)

    text = text.replace(" ","").strip()
    text = text.replace("\\n","").strip()
    text = text.replace("','","").strip()
    text = text.replace("['","").strip()
    text = text.replace("]'","").strip()
    text = text.replace("\t","").strip()
    text = re.sub(r'(.)\1+', r'\1', text)
    # 段落切分
    for para in re.split(r"\n+",text):
        if len(para) <= max_len:
            paras.append(para)
            continue
        current_paras = [para]
        for sep in ["[。！？……]","[；]","[，]"]:
            paras_new = []

            for sentence in current_paras:
                if len(sentence) > max_len:
                   sub_sentence = re.split(sep,sentence)
                   paras_new.extend(sub_sentence)
                else:
                    paras_new.append(sentence)
            current_paras = paras_new
        paras.extend(current_paras)
        parents = [""]*len(paras)
        for i in range(len(paras)):
            left = paras[i - 1] if i - 1 >= 0 else ""
            mid = paras[i]
            right = paras[i + 1] if i + 1 < len(paras) else ""
            parents[i] = left + mid + right
        return [{"child":paras[i],"parent":parents[i]} for i in range(len(paras))]


if __name__ == '__main__':
    datas = sp.read_data("../data/result.md")
    datas = "".join(data for data in datas)
    print(split_text(datas))
