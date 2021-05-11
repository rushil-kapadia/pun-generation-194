from flask import Flask, render_template, request
from main import pun_from_word

app = Flask(__name__)

ret = [" ", " ", " ", " "]

@app.route("/", methods=["GET", "POST"])
def home():
	if request.method == "POST":
		print(request.form)
		print(request.form.get("amount"))
		wrd = request.form.get("amount")
		if not (wrd == ' ' or wrd == ''):
			ret[0] = "loading"
			ret[0], ret[1], ret[2] = pun_from_word(wrd)

	print(ret[0] == " ")
	if not ret[0] == " ":
		ret[3] = "Generated Pun"
	else:
		ret[3] = ""
	return render_template("form.html", entries=ret)

# @app.route("/pun")
# def show_pun():
# 	return render_template("pun.html", entries=pun)