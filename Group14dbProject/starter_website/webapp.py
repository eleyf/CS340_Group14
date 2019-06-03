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

# *********************************
# search webapps
# *********************************

@webapp.route('/songSearch.html', methods=['POST','GET'])
def songSearch():
    if request.method == 'GET':
        print("Fetching and rendering song web page")
        db_connection = connect_to_database()
        query = 'SELECT `song`.`id`, `song`.`name` AS `song_name`, \
                `album`.`name` AS `album_name`, \
                `artist`.`name` AS `artist_name` \
                FROM `song`\
                JOIN `album` on `song`.`album_id` = `album`.`id`\
                JOIN `song_artist` on `song`.`id` = `song_artist`.`song_id`\
                JOIN `artist` ON `song_artist`.`artist_id` = `artist`.`id`\
                ORDER BY song_id ASC;'
        result = execute_query(db_connection, query).fetchall();
        print(result)

        result = list(result)
        lead = 1;
        tail = 0;
        if len(result) > 1:
            while lead < len(result) and result[lead][0] == result[tail][0]:
                lead += 1
            # tail is at the start of the range to condense
            # lead is at the end of the range to condense (exclusive)
            condensed = list(result[tail])
            condensed[3] = [condensed[3]]

            for i in range(tail + 1, lead):
                condensed[3].append(result[i][3])

            result[tail:lead] = [condensed]

        result.sort(key = lambda x: x[1])
        return render_template('songSearch.html', rows=result)
    elif request.method == 'POST':
        print("Fetching and rendering song web page post")
        db_connection = connect_to_database()
        songToSearchFor = request.form['songToSearchFor']
        query = "SELECT `song`.`id`, `song`.`name` AS `song_name`,\
                `album`.`name` AS `album_name`,\
                `artist`.`name` AS `artist_name` \
                FROM `song`\
                JOIN `album` on `song`.`album_id` = `album`.`id`\
                JOIN `song_artist` on `song`.`id` = `song_artist`.`song_id`\
                JOIN `artist` ON `song_artist`.`artist_id` = `artist`.`id` \
                WHERE `song`.`name` LIKE %s \
                ORDER BY song_name ASC"
        data = ("%" + songToSearchFor + "%",)
        result = execute_query(db_connection, query, data).fetchall();
        print(result)

        result = list(result)

        lead = 1;
        tail = 0;
        if len(result) > 1:
            while lead < len(result) and result[lead][0] == result[tail][0]:
                lead += 1
            # tail is at the start of the range to condense
            # lead is at the end of the range to condense (exclusive)
            condensed = list(result[tail])
            condensed[3] = [condensed[3]]

            for i in range(tail + 1, lead):
                condensed[3].append(result[i][3])

            result[tail:lead] = [condensed]

        result.sort(key = lambda x: x[1])
        
        return render_template('songSearch.html', rows=result)

@webapp.route('/albumSearch.html', methods=['POST','GET'])
def albumSearch():
    if request.method == 'GET':
        print("Fetching and rendering album web page")
        db_connection = connect_to_database()
        query = 'SELECT `album`.`id`, `album`.`name`, \
                `record_label`.`name`, `album`.`release_date` \
                FROM `album`\
                JOIN `record_label` ON `album`.`label_id` = `record_label`.`id` \
                ORDER BY `album`.`name` ASC;'
        result = execute_query(db_connection, query).fetchall();
        print(result)
        return render_template('albumSearch.html', rows=result)

    elif request.method == 'POST':
        print("Fetching and rendering album web page post")
        db_connection = connect_to_database()
        albumToSearchFor = request.form['albumToSearchFor']
        query = "SELECT `album`.`id`, `album`.`name`, \
                `record_label`.`name`, `album`.`release_date` \
                FROM `album`\
                JOIN `record_label` ON `album`.`label_id` = `record_label`.`id` \
                WHERE `album`.`name` LIKE %s \
                ORDER BY `album`.`name` ASC;"
        data = ("%" + albumToSearchFor + "%",)
        result = execute_query(db_connection, query, data).fetchall();
        print(result)
        return render_template('albumSearch.html', rows=result)

@webapp.route('/artistSearch.html', methods=['POST','GET'])
def artistSearch():
    if request.method == 'GET':
        print("Fetching and rendering artist web page")
        db_connection = connect_to_database()
        query = 'SELECT * FROM `artist` ORDER BY name ASC;'
        result = execute_query(db_connection, query).fetchall();
        print(result)
        return render_template('artistSearch.html', rows=result)

    elif request.method == 'POST':
        print("Fetching and rendering artist web page post")
        db_connection = connect_to_database()
        artistToSearchFor = request.form['artistToSearchFor']
        query = "SELECT * FROM `artist` \
                WHERE `artist`.`name` LIKE %s\
                ORDER BY name ASC;"
        data = ("%" + artistToSearchFor + "%",)
        result = execute_query(db_connection, query, data).fetchall();
        print(result)
        return render_template('artistSearch.html', rows=result)

@webapp.route('/labelSearch.html', methods=['POST','GET'])
def labelSearch():
    if request.method == 'GET':
        print("Fetching and rendering label web page")
        db_connection = connect_to_database()
        query = 'SELECT * FROM `record_label` ORDER BY name ASC;'
        result = execute_query(db_connection, query).fetchall();
        print(result)
        return render_template('labelSearch.html', rows=result)

    elif request.method == 'POST':
        print("Fetching and rendering label web page post")
        db_connection = connect_to_database()
        labelToSearchFor = request.form['labelToSearchFor']
        query = "SELECT * FROM `record_label`\
                WHERE `record_label`.`name` LIKE %s\
                ORDER BY name ASC;"
        data = ("%" + labelToSearchFor + "%",)
        result = execute_query(db_connection, query, data).fetchall();
        print(result)
        return render_template('labelSearch.html', rows=result)

# *********************************
# add webapps
# *********************************

@webapp.route('/songAdd.html', methods=['GET', 'POST'])
def songAdd():
    if request.method == 'GET':
        db_connection = connect_to_database()

        query = 'SELECT `album`.`name` FROM `album`'
        album_result = execute_query(db_connection, query).fetchall()

        query = 'SELECT `artist`.`name` FROM `artist`'
        artist_result = execute_query(db_connection, query).fetchall()

        result = {
            'album_result': album_result,
            'artist_result': artist_result
        }

        return render_template('songAdd.html', rows=result)

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



        artist_keys = [s for s in request.form if 'artistName' in s]
        artist_keys.pop()

        # get the artist ids given the artist names
        data = tuple([request.form[s] for s in request.form if 'artistName' in s])

        query = 'SELECT `artist`.`id` FROM `artist` WHERE `artist`.`name` = %s'

        for artist_key in artist_keys:
            query += ' OR `artist`.`name` = %s'

        result = execute_query(db_connection, query, data).fetchall()

        artist_ids = []

        try:
            for data_pair in result:
                artist_ids.append(data_pair[0])
        except IndexError:
            errors.append('Invalid artist')

        if errors:
            return render_template('songAdd.html', errors=errors)

        # insert data
        query = ('INSERT INTO `song` (`id`, `name`, `album_id`) '
                 'VALUES (NULL, %s, %s);')
        data = (song_name, album_id)
        execute_query(db_connection, query, data)

        for artist_id in artist_ids:
            query = ('INSERT INTO `song_artist` (`song_id`, `artist_id`) '
                     'VALUES (LAST_INSERT_ID(), %s);')
            data = (artist_id,)
            execute_query(db_connection, query, data)

        # display search page
        query = 'SELECT `song`.`id`, `song`.`name` AS `song_name`, `album`.`name` AS `album_name`, `artist`.`name` AS `artist_name` FROM `song`JOIN `album` on `song`.`album_id` = `album`.`id`JOIN `song_artist` on `song`.`id` = `song_artist`.`song_id`JOIN `artist` ON `song_artist`.`artist_id` = `artist`.`id` ORDER BY song_name ASC;'
        result = execute_query(db_connection, query).fetchall();
        return render_template('songSearch.html', rows=result)

@webapp.route('/albumAdd.html', methods=['GET', 'POST'])
def albumAdd():
    if request.method == 'GET':

        db_connection = connect_to_database()

        query = 'SELECT `record_label`.`name` FROM `record_label`'
        label_result = execute_query(db_connection, query).fetchall()

        query = 'SELECT `artist`.`name` FROM `artist`'
        artist_result = execute_query(db_connection, query).fetchall()

        result = {
            'label_result': label_result,
            'artist_result': artist_result
        }

        return render_template('albumAdd.html', rows=result)
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

        artist_keys = [s for s in request.form if 'artistName' in s]
        artist_keys.pop()

        # get the artist ids given the artist names
        data = tuple([request.form[s] for s in request.form if 'artistName' in s])

        query = 'SELECT `artist`.`id` FROM `artist` WHERE `artist`.`name` = %s'

        for artist_key in artist_keys:
            query += ' OR `artist`.`name` = %s'

        result = execute_query(db_connection, query, data).fetchall()

        artist_ids = []

        try:
            for data_pair in result:
                artist_ids.append(data_pair[0])
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

        for artist_id in artist_ids:
            query = ('INSERT INTO `album_artist` (`album_id`, `artist_id`) '
                     'VALUES (LAST_INSERT_ID(), %s);')
            data = (artist_id,)
            execute_query(db_connection, query, data)

        # display search page
        query = 'SELECT `album`.`id`, `album`.`name`, `record_label`.`name`, `album`.`release_date` FROM `album`JOIN `record_label` ON `album`.`label_id` = `record_label`.`id` ORDER BY `album`.`name` ASC;'
        result = execute_query(db_connection, query).fetchall()
        return render_template('albumSearch.html', rows=result)

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

# *********************************
# edit webapps
# *********************************

@webapp.route('/songEdit.html/<int:id>', methods=['POST','GET'])
def songEdit(id):
    if request.method == 'GET':
        db_connection = connect_to_database()
        song_query = "SELECT `song`.`id`, `song`.`name` AS `song_name`, \
                `album`.`id` AS `album_id`, \
                `album`.`name` AS `album_name` \
                FROM `song`\
                JOIN `album` on `song`.`album_id` = `album`.`id`\
                JOIN `song_artist` on `song`.`id` = `song_artist`.`song_id`\
                JOIN `artist` ON `song_artist`.`artist_id` = `artist`.`id`\
                WHERE `song`.`id` = %s"
        data = (id,)
        song_result = execute_query(db_connection, song_query, data).fetchone();
        print(song_result)

        album_query = 'SELECT `id`, `name` from `album` ORDER BY `name` ASC'
        album_results = execute_query(db_connection, album_query).fetchall();
        print(album_results)

        return render_template('songEdit.html', song_info = song_result, album_info = album_results)
    elif request.method == 'POST':
        print("Update song!");
        # get data from form
        songNameEdit = request.form['songNameEdit']
        albumEdit = request.form['albumEdit']

        # connect to database and update
        db_connection = connect_to_database()

        query = "UPDATE `song`\
                SET `song`.`name` = %s,\
                `song`.`album_id` = (SELECT `album`.`id` FROM `album` WHERE `album`.`name` = %s)\
                WHERE `song`.`id` = %s"
        data = (songNameEdit, albumEdit, id)
        result = execute_query(db_connection, query, data)


        return redirect('/songSearch.html')


@webapp.route('/albumEdit.html/<int:id>', methods=['POST','GET'])
def albumEdit(id):
    if request.method == 'GET':
        db_connection = connect_to_database()
        album_query = "SELECT `album`.`id`, `album`.`name`, \
                `record_label`.`id`, `album`.`release_date` \
                FROM `album`\
                JOIN `record_label` ON `album`.`label_id` = `record_label`.`id` \
                WHERE `album`.`id` = %s"
        data = (id,)
        album_result = execute_query(db_connection, album_query, data).fetchone();
        print(album_result)

        label_query = 'SELECT `id`, `name` from `record_label` ORDER BY `name` ASC'
        label_results = execute_query(db_connection, label_query).fetchall();
        print(label_results)

        return render_template('albumEdit.html', album_info = album_result, label_info = label_results)
    elif request.method == 'POST':
        print("Update album!");
        # get data from form
        albumNameEdit = request.form['albumNameEdit']
        labelEdit = request.form['labelEdit']
        releaseDateEdit = request.form['releaseDateEdit']

        # connect to database and update
        db_connection = connect_to_database()

        query = "UPDATE `album`\
                SET `album`.`name` = %s,\
                `album`.`label_id` = (SELECT `record_label`.`id` FROM `record_label` WHERE `record_label`.`name` = %s), `album`.`release_date` = %s\
                WHERE `album`.`id` = %s"
        data = (albumNameEdit, labelEdit, releaseDateEdit, id)
        result = execute_query(db_connection, query, data)


        return redirect('/albumSearch.html')


@webapp.route('/artistEdit.html/<int:id>', methods=['POST','GET'])
def artistEdit(id):
    if request.method == 'GET':
        db_connection = connect_to_database()
        artist_query = "SELECT * FROM `artist`\
                WHERE `id` = %s"
        data = (id,)
        artist_result = execute_query(db_connection, artist_query, data).fetchone();
        print(artist_result)
        return render_template('artistEdit.html', artist_info = artist_result)
    elif request.method == 'POST':
        print("Update artist!");
        # get data from form
        artistNameEdit = request.form['artistNameEdit']

        # connect to database and update
        db_connection = connect_to_database()
        query = "UPDATE `artist`\
                SET `name` = %s\
                WHERE `id` = %s"
        data = (artistNameEdit, id)
        result = execute_query(db_connection, query, data)


        return redirect('/artistSearch.html')

@webapp.route('/labelEdit.html/<int:id>', methods=['POST','GET'])
def labelEdit(id):
    if request.method == 'GET':
        db_connection = connect_to_database()
        label_query = "SELECT * FROM `record_label`\
                WHERE `id` = %s"
        data = (id,)
        label_result = execute_query(db_connection, label_query, data).fetchone();
        print(label_result)
        return render_template('labelEdit.html', label_info = label_result)
    elif request.method == 'POST':
        print("Update label!");
        # get data from form
        labelNameEdit = request.form['labelNameEdit']
        streetAddressEdit = request.form['streetAddressEdit']
        cityEdit = request.form['cityEdit']
        stateEdit = request.form['stateEdit']
        zipCodeEdit = request.form['zipCodeEdit']

        # connect to database and update
        db_connection = connect_to_database()
        query = "UPDATE `record_label`\
                SET `name` = %s, `street_address` = %s, `city` = %s, `state` = %s, `zip_code` = %s\
                WHERE `id` = %s"
        data = (labelNameEdit, streetAddressEdit, cityEdit, stateEdit, zipCodeEdit, id)
        result = execute_query(db_connection, query, data)


        return redirect('/labelSearch.html')


# *********************************
# delete webapps
# *********************************

@webapp.route('/songDelete/<int:id>')
def songDelete(id):
    db_connection = connect_to_database()
    query = "DELETE FROM `song` WHERE `id` = %s"
    data = (id,)
    result = execute_query(db_connection, query, data)
    return redirect('/songSearch.html')


@webapp.route('/albumDelete/<int:id>')
def albumDelete(id):
    db_connection = connect_to_database()
    query = "DELETE FROM `album` WHERE `id` = %s"
    data = (id,)
    result = execute_query(db_connection, query, data)
    return redirect('/albumSearch.html')

@webapp.route('/artistDelete/<int:id>')
def artistDelete(id):
    db_connection = connect_to_database()
    query = "DELETE FROM `artist` WHERE `id` = %s"
    data = (id,)
    result = execute_query(db_connection, query, data)
    return redirect('/artistSearch.html')

@webapp.route('/labelDelete/<int:id>')
def labelDelete(id):
    db_connection = connect_to_database()
    query = "DELETE FROM `record_label` WHERE `id` = %s"
    data = (id,)
    result = execute_query(db_connection, query, data)
    return redirect('/labelSearch.html')
