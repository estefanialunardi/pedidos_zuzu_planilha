from collections import defaultdict
from pathlib import Path
import sqlite3

import streamlit as st
import altair as alt
import pandas as pd

st.set_page_config(
    page_title='Acompanhamento de pedidos Zuzu',
    page_icon=':shopping_bags:',
)


def connect_db():
    '''Connects to the sqlite database.'''

    DB_FILENAME = Path(__file__).parent/'inventory.db'
    db_already_exists = DB_FILENAME.exists()

    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists

    return conn, db_was_just_created


def initialize_data(conn):
    #connect_to_tunnel_and_mysqlserver  
        db_server = st.secrets["db_server"]
        user = st.secrets["user"]
        db_port = st.secrets["db_port"]
        password = st.secrets["password"]
        ip = st.secrets["ip"]
        db_name = st.secrets["db_name"]
        ip_ssh = st.secrets["ip_ssh"]
        ssh_username = st.secrets["ssh_username"]
        ssh_password = st.secrets["ssh_password"]
        try:
            server = SSHTunnelForwarder((ip_ssh, 4242), ssh_username=ssh_username, ssh_password=ssh_password, remote_bind_address=(db_server, 3306))
            server.start()
            port = str(server.local_bind_port)
            conn_addr = 'mysql://' + user + ':' + password + '@' + db_server + ':' + port + '/' + db_name
            engine = create_engine(conn_addr)
            connection = engine.connect()
            trans = connection.begin()
            st.success("Connected!")
        except:
            st.error("Erro de conexão")



        try:
            my_email= st.secrets["my_email"]
            mail_password= st.secrets["mail_password"]
            msg=MIMEText(f"""{name} , 
            votre inscription à Attitude Corps et Danses a été reçue! En cas de problème concernant les informations ou les fichiers fournis, nous vous contacterons !
            L’entrée de l’école se fera par le 11 Rue Gabriel Péri, 31000 Toulousee. Veuillez utiliser ces codes pour rentrer à l’immeuble.
            Code: 1311
            À très vite, """)
            msg['From'] = my_email
            msg['To'] = mail
            msg['Subject']= f" {name}, votre inscription à Attitude Corps et Danses !"
            mail_server = smtplib.SMTP_SSL('smtp.gmail.com' ,465)
            mail_server.ehlo()
            mail_server.login(my_email, mail_password)
            mail_server.sendmail(msg["From"], msg["To"], msg.as_string())
            st.success("Merci! Rendez-vous en classe !")
            st.balloons()
        except Exception as er:
            st.write(er)

        try:
            from sqlalchemy import text
            mySql_insert_query0 = f"""UPDATE elevesdf set name = '{name}', birthday='{birthday}', age='{age}', address='{address}', city='{city}', toulouse = '{toulouse}', cpode='{pcode}',lat='{lat}',long='{lon}', mail='{mail}', telephone = '{telephone}', legal_representative= '{legal_representative}' where `name` = '{name}'"""
            connection.execute(text(mySql_insert_query0))
            st.spinner(text="S'il vous plaît, attendez !")
        except: 
            st.error("Erro de conexão")




def update_data(conn, df, changes):
    '''Updates the inventory data in the database.'''
    cursor = conn.cursor()

    if changes['edited_rows']:
        deltas = st.session_state.inventory_table['edited_rows']
        rows = []

        for i, delta in deltas.items():
            row_dict = df.iloc[i].to_dict()
            row_dict.update(delta)
            rows.append(row_dict)

        cursor.executemany(
            '''
            UPDATE inventory
            SET
                item_name = :item_name,
                price = :price,
                units_sold = :units_sold,
                units_left = :units_left,
                cost_price = :cost_price,
                reorder_point = :reorder_point,
                description = :description
            WHERE id = :id
            ''',
            rows,
        )

    if changes['added_rows']:
        cursor.executemany(
            '''
            INSERT INTO inventory
                (id, item_name, price, units_sold, units_left, cost_price, reorder_point, description)
            VALUES
                (:id, :item_name, :price, :units_sold, :units_left, :cost_price, :reorder_point, :description)
            ''',
            (defaultdict(lambda: None, row) for row in changes['added_rows']),
        )

    if changes['deleted_rows']:
        cursor.executemany(
            'DELETE FROM inventory WHERE id = :id',
            ({'id': int(df.loc[i, 'id'])} for i in changes['deleted_rows'])
        )

    conn.commit()


# -----------------------------------------------------------------------------
# Draw the actual page, starting with the inventory table.

# Set the title that appears at the top of the page.
'''
# :shopping_bags: Inventory tracker

**Welcome to Alice's Corner Store's intentory tracker!**
This page reads and writes directly from/to our inventory database.
'''

st.info('''
    Use the table below to add, remove, and edit items.
    And don't forget to commit your changes when you're done.
    ''')

# Connect to database and create table if needed
conn, db_was_just_created = connect_db()

# Initialize data.
if db_was_just_created:
    initialize_data(conn)
    st.toast('Database initialized with some sample data.')

# Load data from database
df = load_data(conn)

# Display data with editable table
edited_df = st.data_editor(
    df,
    disabled=['id'], # Don't allow editing the 'id' column.
    num_rows='dynamic', # Allow appending/deleting rows.
    column_config={
        # Show dollar sign before price columns.
        "price": st.column_config.NumberColumn(format="$%.2f"),
        "cost_price": st.column_config.NumberColumn(format="$%.2f"),
    },
    key='inventory_table')

has_uncommitted_changes = any(len(v) for v in st.session_state.inventory_table.values())

st.button(
    'Commit changes',
    type='primary',
    disabled=not has_uncommitted_changes,
    # Update data in database
    on_click=update_data,
    args=(conn, df, st.session_state.inventory_table))


# -----------------------------------------------------------------------------
# Now some cool charts

# Add some space
''
''
''

st.subheader('Units left', divider='red')

need_to_reorder = df[df['units_left'] < df['reorder_point']].loc[:, 'item_name']

if len(need_to_reorder) > 0:
    items = '\n'.join(f'* {name}' for name in need_to_reorder)

    st.error(f"We're running dangerously low on the items below:\n {items}")

''
''

st.altair_chart(
    # Layer 1: Bar chart.
    alt.Chart(df)
        .mark_bar(
            orient='horizontal',
        )
        .encode(
            x='units_left',
            y='item_name',
        )
    # Layer 2: Chart showing the reorder point.
    + alt.Chart(df)
        .mark_point(
            shape='diamond',
            filled=True,
            size=50,
            color='salmon',
            opacity=1,
        )
        .encode(
            x='reorder_point',
            y='item_name',
        )
    ,
    use_container_width=True)

st.caption('NOTE: The :diamonds: location shows the reorder point.')

''
''
''

# -----------------------------------------------------------------------------

st.subheader('Best sellers', divider='orange')

''
''

st.altair_chart(alt.Chart(df)
    .mark_bar(orient='horizontal')
    .encode(
        x='units_sold',
        y=alt.Y('item_name').sort('-x'),
    ),
    use_container_width=True)
