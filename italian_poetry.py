from flask import Flask
from flask import render_template, url_for, request, redirect
import sqlite3
import treetaggerwrapper
import re
import copy

app = Flask(__name__)

@app.route('/')
def main_page():
    main_url = url_for('main_page')
    searsh_url = url_for('serch_page')
    if request.args:
        conn = sqlite3.connect("poetry.db")
        word = request.args['word']
        c = conn.cursor()
        tagger = treetaggerwrapper.TreeTagger(TAGLANG="it", TAGDIR='C:/TreeTagger')
        tags = tagger.tag_text(word)
        tags_arr = tags[0].split('\t')
        lemma = tags_arr[2]
        #word = tags_arr[0]
        pos = tags_arr[1]
        pos = re.findall('[A-Z]+?', pos)
        pos = ''.join(pos)

        c.execute('SELECT * FROM lemma_data WHERE lemma LIKE :lem AND pos LIKE :po',
                       {"lem": lemma, "po": pos})
        row = c.fetchall()
        if row == []:
            result = ['Sorry, there is no such word']

        else:
            docs = row[0][3]
            ind = docs.split(',')
            ind = set(ind)
            result = []
            for el in ind:
                if not el == '':
                    indx = int(el)
                    c.execute('SELECT * FROM poetry_data WHERE ID LIKE :id',
                              {"id": indx})
                    row_2 = c.fetchall()
                    result.append(row_2[0])

            #print(row)
            #print(row_2)
        conn.close()
        return render_template('result.html',
                               result=result, main_url=main_url, searsh_url=searsh_url, word=word)
    return render_template('main_page.html', main_url=main_url, searsh_url=searsh_url)



@app.route('/search')
def serch_page():
    main_url = url_for('main_page')
    searsh_url = url_for('serch_page')
    if request.args:
        auth = request.args['auth']
        date_min = request.args['date_min']
        date_max = request.args['date_max']
        size_min = request.args['size_min']
        size_max = request.args['size_max']
        verse = request.args['verse']

        conn = sqlite3.connect("poetry.db")
        c = conn.cursor()
        zapr = 'SELECT * FROM poetry_data'
        if not auth != '':
            if not 'WHERE' in zapr:
                zapr+=' WHERE '
                zapr+='auth LIKE '
                zapr+=auth
            else:
                zapr += ' AND '
                zapr += 'auth LIKE '
                zapr += auth

        if not verse != '':
            if not 'WHERE' in zapr:
                zapr += ' WHERE '
                zapr += 'verse_size LIKE '
                zapr += verse
            else:
                zapr += ' AND '
                zapr += 'verse_size LIKE '
                zapr += verse
        #print(zapr)
        c.execute(zapr)
        row = c.fetchall()
        clean = copy.deepcopy(row)
        flag = 0
        for el in row:
            if date_min != '0' or date_max != '2000':
                flag = 1
                for i in range(int(date_min), int(date_max)+1):
                    if str(i) in el[4]:
                        flag = 0
            if flag == 1:
                clean.remove(el)
                continue

            if size_min != '0' or size_max != '100':
                flag = 1
                for g in range(int(size_min), int(size_max)+1):
                    if g == el[3]:
                        flag = 0

            if flag == 1:
                clean.remove(el)
                continue
        return render_template('search_res.html',
                               clean=clean, main_url=main_url, searsh_url=searsh_url,
                               auth=auth, date_min = date_min, date_max = date_max,
                               size_min = size_min, size_max = size_max, verse = verse)
    return render_template('search.html', main_url=main_url, searsh_url=searsh_url)


if __name__ == '__main__':
    app.run(debug=True)