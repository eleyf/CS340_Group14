from flask import Flask, render_template
from flask import request, redirect
from db_connector.db_connector import connect_to_database, execute_query
#create the web application
webapp = Flask(__name__)

#provide a route where requests on the web application can be addressed
@webapp.route('/hello')
#provide a view (fancy name for a function) which responds to any requests on this route
def hello():
    return "Hello World!";

@webapp.route('/browse_bsg_people')
#the name of this function is just a cosmetic thing
def browse_people():
    print("Fetching and rendering people web page")
    db_connection = connect_to_database()
    query = 'SELECT fname, lname, homeworld, age, character_id from bsg_people;'
    result = execute_query(db_connection, query).fetchall();
    print(result)
    return render_template('people_browse.html', rows=result)

@webapp.route('/add_new_people', methods=['POST','GET'])
def add_new_people():
    db_connection = connect_to_database()
    if request.method == 'GET':
        query = 'SELECT planet_id, name from bsg_planets'
        result = execute_query(db_connection, query).fetchall();
        print(result)

        return render_template('people_add_new.html', planets = result)
    elif request.method == 'POST':
        print("Add new people!");
        fname = request.form['fname']
        lname = request.form['lname']
        age = request.form['age']
        homeworld = request.form['homeworld']

        query = 'INSERT INTO bsg_people (fname, lname, age, homeworld) VALUES (%s,%s,%s,%s)'
        data = (fname, lname, age, homeworld)
        execute_query(db_connection, query, data)
        return ('Person added!');

@webapp.route('/db-test')
def test_database_connection():
    print("Executing a sample query on the database using the credentials from db_credentials.py")
    db_connection = connect_to_database()
    query = 'SELECT * from bsg_people;'
    result = execute_query(db_connection, query);
    return render_template('db_test.html', rows=result)

#display update form and process any updates, using the same function
@webapp.route('/update_people/<int:id>', methods=['POST','GET'])
def update_people(id):
    db_connection = connect_to_database()
    #display existing data
    if request.method == 'GET':
        people_query = 'SELECT character_id, fname, lname, homeworld, age from bsg_people WHERE character_id = %s' % (id)
        people_result = execute_query(db_connection, people_query).fetchone()

        if people_result == None:
            return "No such person found!"

        planets_query = 'SELECT planet_id, name from bsg_planets'
        planets_results = execute_query(db_connection, planets_query).fetchall();

        return render_template('people_update.html', planets = planets_results, person = people_result)
    elif request.method == 'POST':
        print("Update people!");
        character_id = request.form['character_id']
        fname = request.form['fname']
        lname = request.form['lname']
        age = request.form['age']
        homeworld = request.form['homeworld']

        print(request.form);

        query = "UPDATE bsg_people SET fname = %s, lname = %s, age = %s, homeworld = %s WHERE character_id = %s"
        data = (fname, lname, age, homeworld, character_id)
        result = execute_query(db_connection, query, data)
        print(str(result.rowcount) + " row(s) updated");

        return redirect('/browse_bsg_people')

@webapp.route('/delete_people/<int:id>')
def delete_people(id):
    '''deletes a person with the given id'''
    db_connection = connect_to_database()
    query = "DELETE FROM bsg_people WHERE character_id = %s"
    data = (id,)

    result = execute_query(db_connection, query, data)
    return (str(result.rowcount) + "row deleted")


# *************************************************************** #
#
#   apps for music database below
#
# *************************************************************** #

@webapp.route('/')
def index():
    return render_template('index.html')

@webapp.route('/index.html')
def home():
    return render_template('index.html')

@webapp.route('/songSearch.html')
def songSearch():
    print("Fetching and rendering song web page")
    db_connection = connect_to_database()
    query = 'SELECT `song`.`id`, `song`.`name` AS `song_name`, `album`.`name` AS `album_name`, `artist`.`name` AS `artist_name` FROM `song`JOIN `album` on `song`.`album_id` = `album`.`id`JOIN `song_artist` on `song`.`id` = `song_artist`.`song_id`JOIN `artist` ON `song_artist`.`artist_id` = `artist`.`id` ORDER BY song_name ASC;'
    result = execute_query(db_connection, query).fetchall();
    print(result)
    return render_template('songSearch.html', rows=result)

@webapp.route('/songAdd.html', methods=['GET', 'POST'])
def songAdd():
    if request.method == 'GET':
        return render_template('songAdd.html')
    elif request.method == 'POST':
        db_connection = connect_to_database()
        errors = []

        # extract data from form
        song_name = request.form['songName']
        album_name = request.form['albumName']
        artist_name = request.form['artistName']

        # get the album id given the album name
        data = (album_name,)
        query = 'SELECT `album`.`id` FROM `album` WHERE `album`.`name` = %s;'
        result = execute_query(db_connection, query, data).fetchall()

        try:
            album_id = result[0][0]
        except IndexError:
            errors.append('Invalid album')

        # get the artist id given the artist name
        data = (artist_name,)
        query = 'SELECT `artist`.`id` FROM `artist` WHERE `artist`.`name` = %s;'
        result = execute_query(db_connection, query, data).fetchall()

        try:
            artist_id = result[0][0]
        except IndexError:
            errors.append('Invalid artist')

        if errors:
            return render_template('songAdd.html', errors=errors)

        # insert data
        query = ('INSERT INTO `song` (`id`, `name`, `album_id`) '
                 'VALUES (NULL, %s, %s);')
        data = (song_name, album_id)
        execute_query(db_connection, query, data)

        query = ('INSERT INTO `song_artist` (`song_id`, `artist_id`) '
                 'VALUES (LAST_INSERT_ID(), %s);')
        data = (artist_id,)
        execute_query(db_connection, query, data)

        # display search page
        query = 'SELECT `song`.`id`, `song`.`name` AS `song_name`, `album`.`name` AS `album_name`, `artist`.`name` AS `artist_name` FROM `song`JOIN `album` on `song`.`album_id` = `album`.`id`JOIN `song_artist` on `song`.`id` = `song_artist`.`song_id`JOIN `artist` ON `song_artist`.`artist_id` = `artist`.`id` ORDER BY song_name ASC;'
        result = execute_query(db_connection, query).fetchall();
        return render_template('songSearch.html', rows=result)

@webapp.route('/songEdit.html')
def songEdit():
    return render_template('songEdit.html')

@webapp.route('/albumSearch.html')
def albumSearch():
    print("Fetching and rendering album web page")
    db_connection = connect_to_database()
    query = 'SELECT `album`.`id`, `album`.`name`, `record_label`.`name`, `album`.`release_date` FROM `album`JOIN `record_label` ON `album`.`label_id` = `record_label`.`id` ORDER BY `album`.`name` ASC;'
    result = execute_query(db_connection, query).fetchall();
    print(result)
    return render_template('albumSearch.html', rows=result)

@webapp.route('/albumAdd.html', methods=['GET', 'POST'])
def albumAdd():
    if request.method == 'GET':
        return render_template('albumAdd.html')
    elif request.method == 'POST':
        db_connection = connect_to_database()
        errors = []

        # extract data from form
        album_name = request.form['albumName']
        label_name = request.form['labelName']
        release_date = request.form['releaseDate']
        artist_name = request.form['artistName']

        # get the label id given the label name
        data = (label_name,)
        query = 'SELECT `record_label`.`id` FROM `record_label` WHERE `record_label`.`name` = %s;'
        result = execute_query(db_connection, query, data).fetchall()

        try:
            label_id = result[0][0]
        except IndexError:
            errors.append('Invalid label')

        # get the artist id given the artist name
        data = (artist_name,)
        query = 'SELECT `artist`.`id` FROM `artist` WHERE `artist`.`name` = %s;'
        result = execute_query(db_connection, query, data).fetchall()

        try:
            artist_id = result[0][0]
        except IndexError:
            errors.append('Invalid artist')

        if errors:
            return render_template('albumAdd.html', errors=errors)

        # insert data
        query = ('INSERT INTO `album` '
                 '(`id`, `name`, `label_id`, `release_date`) '
                 'VALUES (NULL, %s, %s, %s);')
        data = (album_name, label_id, release_date)
        result = execute_query(db_connection, query, data)

        query = ('INSERT INTO `album_artist` (`album_id`, `artist_id`) '
                 'VALUES (LAST_INSERT_ID(), %s);')
        data = (artist_id,)
        execute_query(db_connection, query, data)

        # display search page
        query = 'SELECT `album`.`id`, `album`.`name`, `record_label`.`name`, `album`.`release_date` FROM `album`JOIN `record_label` ON `album`.`label_id` = `record_label`.`id` ORDER BY `album`.`name` ASC;'
        result = execute_query(db_connection, query).fetchall()
        return render_template('albumSearch.html', rows=result)

@webapp.route('/albumEdit.html')
def albumEdit():
    return render_template('albumEdit.html')

@webapp.route('/artistSearch.html')
def artistSearch():
    print("Fetching and rendering artist web page")
    db_connection = connect_to_database()
    query = 'SELECT * FROM `artist` ORDER BY name ASC;'
    result = execute_query(db_connection, query).fetchall();
    print(result)
    return render_template('artistSearch.html', rows=result)

@webapp.route('/artistAdd.html', methods=['GET', 'POST'])
def artistAdd():
    if request.method == 'GET':
        return render_template('artistAdd.html')
    elif request.method == 'POST':
        db_connection = connect_to_database()

        # extract data from form
        artist_name = request.form['artistName']

        # insert data
        query = ('INSERT INTO `artist` (`id`, `name`) '
                 'VALUES (NULL, %s);')
        data = (artist_name,)
        execute_query(db_connection, query, data)

        # display search page
        query = 'SELECT * FROM `artist` ORDER BY name ASC;'
        result = execute_query(db_connection, query).fetchall()
        return render_template('artistSearch.html', rows=result)

@webapp.route('/artistEdit.html')
def artistEdit():
    return render_template('artistEdit.html')

@webapp.route('/labelSearch.html')
def labelSearch():
    print("Fetching and rendering label web page")
    db_connection = connect_to_database()
    query = 'SELECT * FROM `record_label` ORDER BY name ASC;'
    result = execute_query(db_connection, query).fetchall();
    print(result)
    return render_template('labelSearch.html', rows=result)

@webapp.route('/labelAdd.html', methods=['GET', 'POST'])
def labelAdd():
    if request.method == 'GET':
        return render_template('labelAdd.html')
    elif request.method == 'POST':
        db_connection = connect_to_database()

        # extract data from form
        label_name = request.form['labelName']
        street_address = request.form['streetAddress']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zipCode']

        # insert data
        query = ('INSERT INTO `record_label` '
                 '(`id`, `name`, `street_address`, `city`, `state`, `zip_code`) '
                 'VALUES (NULL, %s, %s, %s, %s, %s);')
        data = (label_name, street_address, city, state, zip_code)
        execute_query(db_connection, query, data)

        # display search page
        query = 'SELECT * FROM `record_label` ORDER BY name ASC;'
        result = execute_query(db_connection, query).fetchall()
        return render_template('labelSearch.html', rows=result)

@webapp.route('/labelEdit.html')
def labelEdit():
    return render_template('labelEdit.html')
