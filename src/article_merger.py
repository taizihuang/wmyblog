import pandas as pd
from bs4 import BeautifulSoup
import json, re

class ArticleMerger:
    def __init__(self, data_dir, ct_dir):
        self.data_dir = data_dir
        self.ct_dir = ct_dir
        with open(f"{data_dir}/id_dict.json", "r") as f:
            self.id_dict =  json.loads(f.read())
        self.df_article = pd.read_pickle(f"{data_dir}/article_full.pkl")
        self.ct_id_list = list(self.id_dict)
        self.udn_id_list = [id for id in self.df_article["id"] if id not in self.ct_id_list] 
        self.id_list = self.ct_id_list + self.udn_id_list
        with open(f"{data_dir}/correction.json", "r") as f:
            self.correction_dict = json.loads(f.read())
        # self.skip_list = ["181680139", "180085085", "178299171", "178109529", "177490083",
        #                   "177276403", "168244348"]
    
    def load_post(self, art_id):
        if art_id in self.id_dict.keys():
            old_id = self.id_dict[art_id]
            with open(f"{self.ct_dir}/{old_id}.html") as f:
                self.old_post = BeautifulSoup(f.read(), features="lxml")
        else:
            self.old_post = BeautifulSoup("")
        new_post = self.df_article.loc[self.df_article["id"] == art_id, "post"].iloc[0]
        if art_id in self.correction_dict.keys():
            for cor in self.correction_dict[art_id]:
                new_post = new_post.replace(cor["original"], cor["correction"])
        self.new_post = BeautifulSoup(new_post, features="lxml")
    
    def ct_element_check(self):
        # 检查非<p><img>内容
        def content_check(content):
            keyword_list = [
                "伯克三型的升級示意圖",
                "writtenbyronpaul",
                "WhattheMediaWon’t"
            ]
            flag = 0
            content = content.replace(" ", "").replace(" ", "")
            if content == "":
                flag = 1
            for keyword in keyword_list:
                if keyword in content:
                    flag += 1
            return flag

        count = 0
        for art_id in self.ct_id_list:
            self.load_post(art_id)
            for el in self.old_post.p.next_siblings:
                if el.name not in ["p", "img", None]:
                    flag = content_check(el.text)
                    if flag == 0:
                        print(art_id)
                        print(el)
                        count += 1
        if count == 0:
            print("[element check] passed")
    
    def diff_article_text(self, art_id):
        self.load_post(art_id)
        new_p = self.new_post.find_all("p")
        old_p = self.old_post.find(class_="articlebox").find_all("p")

        flag = 1
        if len(new_p) < len(old_p):
            print("paragraph counts not match")
            flag = 0
        else:
            for i in range(len(old_p)):
                new_pa = new_p[i].text
                new_pa = new_pa.replace(" ", "").replace("\r","").replace("\n", "").replace("\u200b", "").replace(" ", "")
                old_pa = old_p[i].text
                old_pa = old_pa.replace(" ", "").replace("\u200b", "").replace("\n", "").replace(" ", "") 

                new_count = len(new_pa)
                old_count = len(old_pa)

                if new_count != old_count:
                    print(f"[{art_id}]\n new p [{i+1}] [{new_count}]: {new_pa}")
                    print(f"[{self.id_dict[art_id]}]\n old p [{i+1}] [{old_count}]: {old_pa}")
                    print("\n")
                    flag = 0
        return flag
    
    def diff_article_image(self, art_id):
        self.load_post(art_id)
        new_img = self.new_post.find_all("img")
        old_img = self.old_post.find(class_="articlebox").find_all("img")

        flag = 1
        if len(new_img) < len(old_img):
            print(f"{art_id} image counts not match")
            flag = 0
        else:
            for i in range(len(old_img)):
                new_src = new_img[i].attrs["src"]
                old_src = old_img[i].attrs["src"] 

                if new_src != old_src:
                    print(f"[{art_id}]\n new p [{i+1}] {new_src}")
                    print(f"[{self.id_dict[art_id]}]\n old p [{i+1}] {old_src}]")
                    print("\n")
                    flag = 0
        return flag
    
    def diff_article_link(self, art_id):
        self.load_post(art_id)
        new_a = self.new_post.find_all("a")
        old_a = self.old_post.find(class_="articlebox").find_all("a")

        flag = 1
        if len(new_a) < len(old_a):
            print(f"{art_id} link counts not match")
            flag = 0
        else:
            for i in range(len(old_a)):
                new_src = new_a[i].attrs["href"] 
                old_src = old_a[i].attrs["href"] 

                if new_src != old_src:
                    print("\n")
                    print(f"[{art_id}]\n new p [{i+1}] {new_src}")
                    print(f"[{self.id_dict[art_id]}]\n old p [{i+1}] {old_src}]")
                    print("\n")
                    flag = 0
        return flag
    
    def ct_diff_text(self):
        count = 0
        for art_id in self.ct_id_list:
            flag = self.diff_article_text(art_id)
            if flag == 0:
                count += 1
        if count == 0:
            print("[diff text] passed")

    def ct_diff_image(self):
        count = 0
        for art_id in self.ct_id_list:
            flag = self.diff_article_image(art_id)
            if flag == 0:
                count += 1
        if count == 0:
            print("[diff image] passed")

    def ct_diff_link(self):
        count = 0
        for art_id in self.ct_id_list:
            flag = self.diff_article_link(art_id)
            if flag == 0:
                count += 1
        if count == 0:
            print("[diff link] passed")
    
    def ct_split_annotation(self, art_id):
        self.load_post(art_id)
        annotation_list = []
        new_p = self.new_post.find_all("p")
        old_p = self.old_post.find(class_="articlebox").find_all("p")

        flag = 0
        for p in old_p:
            if p.text[:3] in ["【後註"]: #, "==="]:
                annotation_list.append(str(p))
                flag = 1
                break
        
        if (flag == 0) and (len(new_p) == len(old_p)):
            return annotation_list

        while p.next_sibling is not None:
            p = p.next_sibling
            if p.text[:3] in ["【後註"]: #, "==="]:
                annotation_list.append(str(p))
            else:
                annotation_list[-1] += str(p)
        
        if len(new_p) > len(old_p):
            for p in new_p[len(old_p):]:
                if p.text[:3] in ["【後註"]: #, "==="]:
                    annotation_list.append(str(p))
                    break
        
            while p.next_sibling is not None:
                p = p.next_sibling
                if p.text[:3] in ["【後註"]: #, "==="]:
                    annotation_list.append(str(p))
                else:
                    annotation_list[-1] += str(p)

        note_list = []
        for annotation in annotation_list:
            note = re.sub(r"<span style=.*?>(.*?)<\/span>", r"\1", annotation)
            note_list.append(note)
        return note_list
    
    def udn_split_annotation(self, art_id):
        self.load_post(art_id)
        annotation_list = []
        new_p = self.new_post.find_all("p")

        if len(new_p) == 0:
            return annotation_list

        flag = 0
        for p in new_p:
            if p.text[:3] in ["【後註"]: #, "==="]:
                annotation_list.append(str(p))
                flag = 1
                break
        
        if flag == 0:
            return annotation_list

        while p.next_sibling is not None:
            p = p.next_sibling
            if p.text[:3] in ["【後註"]: #, "==="]:
                annotation_list.append(str(p))
            else:
                annotation_list[-1] += str(p)

        note_list = []
        for annotation in annotation_list:
            note = re.sub(r"<span style=.*?>(.*?)<\/span>", r"\1", annotation)
            note_list.append(note)
        return note_list
    
    def split_annotation(self, art_id):
        if art_id in self.ct_id_list:
            annotation_list = self.ct_split_annotation(art_id)
        else:
            annotation_list = self.udn_split_annotation(art_id)

        # print("\n\n".join(annotation_list))
        # print(f"{art_id}, {len(annotation_list)}")
        return annotation_list

    def split_post(self, art_id):
        self.load_post(art_id)
        if art_id in self.ct_id_list:
            post = self.old_post
        else:
            post = self.new_post

        content = ""
        if post.find("p") is None:
            if post.find("div"):
                for child in post.div.children:
                    content += str(child)
            elif post.find("span"):
                for child in post.span.children:
                    content += str(child)
            else:
                print("empty content")
            content = f"<p>{content}</p>"
            print(f"{art_id} raw text")
        else:
            p = post.p
            p_sib = post.p.previousSibling
            while p_sib is not None:
                p = p_sib
                p_sib = p_sib.previousSibling
            content += str(p)
            while p.nextSibling is not None:
                p = p.nextSibling
                if p.text[:3] not in ["【後註"]: #, "==="]:
                    content += str(p)
                else:
                    break
        content = content.replace("戦", "戰")
        content = re.sub(r"<span style=.*?>(.*?)<\/span>", r"\1", content)
        return content
    
    def merge_article(self, art_id):
        post = self.split_post(art_id)
        annotation_list = self.split_annotation(art_id)
        merged = post + "".join(annotation_list)
        return merged
    
    def diff_merge_post(self, art_id):
        def format_content(content):
            content = content.replace(" ", "")
            content = content.replace(" ", "")
            content = content.replace("\r","")
            content = content.replace("\n", "")
            content = content.replace("\u200b", "")
            return content
        merged = self.merge_article(art_id)
        merged = BeautifulSoup(merged, features="lxml")
        new_pa = format_content(self.new_post.text)
        old_pa = format_content(merged.text)
        if abs(len(new_pa) - len(old_pa)) > 0:
            print(art_id)
            print(len(new_pa))
            print(len(old_pa))
    
    def print_element(self, art_id):
        self.load_post(art_id)
        for a in self.new_post.find_all("a"):
            print(a)

if __name__ == "__main__":
    data_dir = "./data"
    ct_dir = "./ct_article"
    merger = ArticleMerger(data_dir, ct_dir)
    # merger.ct_element_check()
    # merger.ct_diff_text()
    # merger.ct_diff_image()
    # merger.ct_diff_link()

    for art_id in merger.id_list:
        merger.diff_merge_post(art_id)
    #     merger.print_element(art_id)
