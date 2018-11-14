# text_me_project
**********

Installation:

run pip install -r requirements.txt
python2 manage.py makemigrations
python2 manage.py migrate
python2 manage.py createsuperuser
python2 manage.py runserver

**********
Useful routes to work with the project:


    ------/users/:

    GET: /users/ lists all users (admins only)
    POST: /users/ takes "email" and "password" as arguments, creates a new User and KartUser
    GET: /users/<id> shows the user identified by id (only available to yourself)
    PUT: /users/<id> updates the user password or email (only available to yourself)
    DELETE: /users/<id> deletes the user

    -----/kartusers/:

    GET: /kartusers/ -lists all kartusers (admins only)
    POST: /kartusers/ -takes "email" and "password" as arguments, creates a new KartUser (not recommended, admins only)
    GET: /kartusers/<id> -shows the kartuser identified by id and his properties(only available to yourself or admin)
    PUT: /users/<id> -updates the kartuser name, bookings (admin only) balance (yourself or admin only)
    DELETE: /users/<id> -deletes the kartuser (admin only)

    -----/bookings/:
    GET: /bookings/ -list all bookings (admins only)
    POST: /bookings/ -create a booking (admins only, not recommended)
    PUT: /bookings/ -update a booking (admins only)
    DELETE: /bookings/ -delete a booking (admins only)
    POST: /bookings/add_booking -creates a booking, with (begin_date, end_date, karts_id) as arguments of POST,
                                if the user has enough money and the booking does not overlap another booking
    POST: /bookings/<id>/update_booking -updates a booking withi d provided and (begin_date, end_date) as POST                                      arguments if the user has enough money and the new booking does not overlap another                                 booking
    
    -----/karts/:
    GET: /karts/ -list all karts (admins only)
    POST: /karts/ -create a kart (admins only)
    PUT: /karts/ -update a kart (admins only)
    POST: /karts/availablekarts -find all available karts between (begin_date,end_date) ordered by distance to karts                                (latitude and longitude are provided in the GET)

    ----/api-token-auth/:
    POST: /api-token-auth/ -get token from auth when providing (email, password)

    ----/api-token-auth-refresh/:
    POST: /api-token-auth-refresh/ -refresh the token when providing (token)

