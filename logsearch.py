from flask import Flask, request, render_template, escape
from flask_bootstrap import Bootstrap
import os

log_path = 'log'
context_lines = 5
page_count = 20

app = Flask(__name__)
Bootstrap(app)


def highlight(text, keywords):
    text = str(escape(text))
    for k in keywords:
        k = str(escape(k))
        text = text.replace(k, '<span style="color: red;font-weight: bold;">' + k + '</span>')
    return text


def context(lines, line_no, keywords):
    start = line_no - context_lines // 2
    end = line_no + context_lines // 2 + 1
    if start < 0:
        start = 0
    if end > len(lines):
        end = len(lines)
    return '<br>'.join(['<code>' + str(i + 1) + '</code>&nbsp;' +
                        highlight(lines[i].strip(), keywords) for i in range(start, end)])


def search(keywords, page):
    cnt = 0
    results = []
    for root, dirs, files in os.walk(log_path):
        for name in files:
            filename = os.path.join(root, name)
            lines = open(filename).readlines()
            for i, line in enumerate(lines):
                if all(k in line for k in keywords):
                    if cnt >= page * page_count:
                        return results, True
                    if cnt >= (page - 1) * page_count:
                        results.append((filename, context(lines, i, keywords)))
                    cnt += 1
    return results, False


@app.route('/')
def logsearch():
    s = request.args.get('s')
    p = int(request.args.get('p') or '1')
    results = None
    previouspage = None
    nextpage = None
    if s:
        keywords = s.split()
        results, nextpage = search(keywords, p)
        nextpage = p + 1 if nextpage else None
        previouspage = p - 1 if p > 1 else None
        start = (p - 1) * page_count + 1
        end = start + len(results) - 1
    return render_template('search.html', results=results, previouspage=previouspage, nextpage=nextpage, s=s,
                           start=start, end=end)


if __name__ == '__main__':
    app.run(threaded=True, debug=True)
