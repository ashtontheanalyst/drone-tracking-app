'''
This is a page full of commented functions and things that could be used
in the future and I don't want cluttering up the main files
'''

'''
This was in the views.py file:

# This is a dynamic page <argument>, changes as the url argument changes
# If you put a name in the URL, index.html will change to match, if not it defaults to above
@views.route("<username>") #i.e. 127.0.0.1:8000/Johnny
def profile(username):
    return render_template("index.html", name=username)



# Similar to above but uses it as a query from the URL
# Also, the page is 'profile.html' which is an inherited page from 'index.html'
# It's exactly the same page but has different content in it
@views.route("/users") #i.e. 127.0.0.1:8000/users?name=Joe
def users():
    args = request.args
    name = args.get('name')
    return render_template("profile.html", name=name)


# Return JSON instead of HTML to the webpage
@views.route("/json")
def get_json():
    return jsonify({'name' : 'Ashton', 'age' : 21})


# Redirect to a diff page
@views.route("/go-to-home")
def go_to_home():
    # If someone tries going to .../go-to-home it'll send them to .../ our home page
    return redirect(url_for("views.home"))'
'''

'''
This is a file that used to be called profile.html, based on index.html:

<!-- This page will look EXACTLT like index.html but with different content
in the content block -->

{% extends "index.html" %}
{% block content %}
<h1>This is the profile page</h1>
<p>Hello {{name}}! Nothing else to see here yet </p>
{% endblock %}
'''