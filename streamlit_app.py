from collections import defaultdict
from pathlib import Path
import sqlite3

import streamlit as st
import altair as alt
import pandas as pd

# -----------------------------------------------------------------------------
# Declare some useful functions.
def connect_db_customers():
    '''Connects to the sqlite database.'''

    DB_FILENAME = Path(__file__).parent/'customers_list.'
    db_already_exists = DB_FILENAME.exists()

    conn_customer = sqlite3.connect(DB_FILENAME)
    db_was_just_created_customer = not db_already_exists

    return conn_customer, db_was_just_created_customer


def initialize_customer_data(conn_customer):
    '''Initializes the customer table with some data.'''
    st.success("Initializing the customer table with some data")
    cursor = conn_customer.cursor()

    st.success("Creating Customer table")
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS customers_list(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            customer_phone TEXT,
            customer_address TEXT,
            customer_birthday TEXT)
        '''
    )

    st.success("Inserting customer data into table")
    cursor.execute(
        '''
        INSERT INTO customers_list
            (customer_name, customer_phone, customer_address, customer_birthday)
        VALUES
            ('Estefânia Mesquita', '11934111604', 'Rua Rio Doce, 124, São Lucas', '16/04')
        '''
    )
    conn_customer.commit()
    st.success("Customer table loaded")


def load_customer_data(conn_customer):
    st.success("Loads the customers_list data from DB!")
    '''Loads the customers_list data from the database.'''
    cursor = conn_customer.cursor()

    try:
        cursor.execute('SELECT * FROM customers_list')
        data = cursor.fetchall()
        st.success("Customers in DB!")
    except:
        return st.write("Error in Customers DB!")

    df_customer = pd.DataFrame(data,
        columns=[
            'id',
            'customer_name',
            'customer_phone',
            'customer_address',
            'customer_birthday'
        ])

    return df_customer

def update_customer_data(conn_customer, df_customer, changes):
    '''Updates the customer data in the database.'''
    cursor = conn_customer.cursor()

    if changes['edited_rows']:
        deltas = st.session_state.customers_list['edited_rows']
        rows = []

        for i, delta in deltas.items():
            row_dict = df_customer.iloc[i].to_dict()
            row_dict.update(delta)
            rows.append(row_dict)

        cursor.executemany(
            '''
            UPDATE customers_list
            SET
                customer_name = :customer_name,
                customer_phone = :customer_phone,
                customer_address = :customer_address,
                customer_birthday = :customer_birthday,
            WHERE id = :id
            ''',
            rows,
        )

    if changes['added_rows']:
        cursor.executemany(
            '''
            INSERT INTO customers_list
                (id, customer_name, customer_phone, customer_address, customer_birthday)
            VALUES
                (:id, :customer_name, :customer_phone, :customer_address, :customer_birthday)
            ''',
            (defaultdict(lambda: None, row) for row in changes['added_rows']),
        )

    if changes['deleted_rows']:
        cursor.executemany(
            'DELETE FROM customers_list WHERE id = :id',
            ({'id': int(df_customer.loc[i, 'id'])} for i in changes['deleted_rows'])
        )

    conn_customer.commit()


# -----------------------------------------------------------------------------
# Draw the actual page, starting with the customer table.

# Set the title that appears at the top of the page.
'''
# :shopping_bags: Pedidos Zuzunely

**Inventário e controle de pedidos**'''

st.info('''
    Tabela de Clientes
    ''')

# Connect to database and create table if needed
conn_customer, db_was_just_created_customer = connect_db_customers()

# Initialize data.
if db_was_just_created_customer:
    initialize_customer_data(conn_customer)
    st.toast('Database initialized with some sample data.')

# Load data from database
df_customer = load_customer_data(conn_customer)

edited_df_customer = st.data_editor(
    df_customer,
    disabled=['id'], # Don't allow editing the 'id' column.
    num_rows='dynamic', # Allow appending/deleting rows.
    # column_config={
    #     # Show dollar sign before price columns.
    #     "price": st.column_config.NumberColumn(format="R$%.2f"),
    #     "cost_price": st.column_config.NumberColumn(format="R$%.2f"),
    # },
    key='customers_list')

st.button(
    'Commit Customer changes',
    type='primary',
    # Update data in database
    on_click=update_customer_data,
    args=(conn_customer, df_customer, st.session_state.customers_list))

st.write(df_customer)

def connect_db():
    '''Connects to the sqlite database.'''

    DB_FILENAME = Path(__file__).parent/'order_inventory.'
    db_already_exists = DB_FILENAME.exists()

    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists

    return conn, db_was_just_created


def initialize_data(conn):
    '''Initializes the inventory table with some data.'''
    st.success("Initializing the inventory table with some data")
    cursor = conn.cursor()

    st.success("Creating table")
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS order_inventory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            price REAL,
            units_sold INTEGER,
            units_left INTEGER,
            cost_price REAL,
            item_campaing TEXT)
        '''
    )

    st.success("Inserting data into table")
    cursor.execute(
        '''
        INSERT INTO order_inventory
            (item_name, price, units_sold, units_left, cost_price, item_campaing)
        VALUES
            ('Muffin de milho', 8, 0, 0, 0, 'Festa Junina'),
            ('Pão de Torresmo', 38, 0, 0, 0, 'Festa Junina'),
            ('Cinnamon Roll', 8, 0, 0, 0, 'Festa Junina'),
            ('Cachorro-Quente assado', 8, 0, 0, 0, 'Festa Junina'),
            ('Praliné de amendoim Pequeno', 5, 0, 0, 0, 'Festa Junina'),
            ('Praliné de amendoim Grande', 10, 0, 0, 0, 'Festa Junina'),
            ('Pipoca Doce Grande', 10, 0, 0, 0, 'Festa Junina'),
            ('Pipoca Doce Pequena', 5, 0, 0, 0, 'Festa Junina'),
            ('Canjica Doce 300mg', 15, 0, 0, 0, 'Festa Junina'),
            ('Canjica Doce 500mg', 25, 0, 0, 0, 'Festa Junina'),
            ('Canjica Doce 1000mg', 50, 0, 0, 0, 'Festa Junina'),
            ('Caldo de Mandioca 300mg', 21, 0, 0, 0, 'Festa Junina'),
            ('Caldo de Mandioca 500mg', 35, 0, 0, 0, 'Festa Junina'),
            ('Caldo de Mandioca 1000mg', 70, 0, 0, 0, 'Festa Junina'),
            ('Caldo de Feijão 300mg', 21, 0, 0, 0, 'Festa Junina'),
            ('Caldo de Feijão 500mg', 35, 0, 0, 0, 'Festa Junina'),
            ('Caldo de Feijão 1000mg', 70, 0, 0, 0, 'Festa Junina'),
            ('Empadão de Carne Seca', 30, 0, 0, 0, 'Festa Junina'),
            ('Bolo de mexerica', 20, 0, 0, 0, 'Festa Junina'),
            ('Bolo de aipim com coco', 20, 0, 0, 0, 'Festa Junina'),
            ('Muffin de mirtilo', 12, 0, 0, 0, 'Fornada'),
            ('Sourdough branco', 30, 0, 0, 0, 'Fornada'),
            ('Sourdough centeio e castanha', 38, 0, 0, 0, 'Fornada'),
            ('Sourdough de Matcha com uva assada', 38, 0, 0, 0, 'Fornada'),
            ('Bagel de flor de sal', 8, 0, 0, 0, 'Fornada'),
            ('Bagel de Papoula', 10, 0, 0, 0, 'Fornada'),
            ('Bagel de Cebola', 10, 0, 0, 0, 'Fornada')
        '''
    )
    conn.commit()
    st.success("Table loaded")


def load_data(conn):
    '''Loads the order_inventory data from the database.'''
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM order_inventory')
        data = cursor.fetchall()
        st.success("Inventory in DB!")
    except:
        return st.write("Error in DB!")

    df = pd.DataFrame(data,
        columns=[
            'id',
            'item_name',
            'price',
            'units_sold',
            'units_left',
            'cost_price',
            'item_campaing'
        ])

    return df

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
            UPDATE order_inventory
            SET
                item_name = :item_name,
                price = :price,
                units_sold = :units_sold,
                units_left = :units_left,
                cost_price = :cost_price,
            WHERE id = :id
            ''',
            rows,
        )

    if changes['added_rows']:
        cursor.executemany(
            '''
            INSERT INTO order_inventory
                (id, item_name, price, units_sold, units_left, cost_price)
            VALUES
                (:id, :item_name, :price, :units_sold, :units_left, :cost_price)
            ''',
            (defaultdict(lambda: None, row) for row in changes['added_rows']),
        )

    if changes['deleted_rows']:
        cursor.executemany(
            'DELETE FROM order_inventory WHERE id = :id',
            ({'id': int(df.loc[i, 'id'])} for i in changes['deleted_rows'])
        )

    conn.commit()


# -----------------------------------------------------------------------------
# Draw the actual page, starting with the inventory table.

# Set the title that appears at the top of the page.
'''
# :shopping_bags: Pedidos Zuzunely

**Inventário e controle de pedidos**'''

st.info('''
    Tabela de controle do estoque, para adicionar, remover ou editar os itens.
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
        "price": st.column_config.NumberColumn(format="R$%.2f"),
        "cost_price": st.column_config.NumberColumn(format="R$%.2f"),
    },
    key='inventory_table')

has_uncommitted_changes = any(len(v) for v in st.session_state.inventory_table.values())

st.button(
    'Commit Inventory changes',
    type='primary',
    disabled=not has_uncommitted_changes,
    # Update data in database
    on_click=update_data,
    args=(conn, df, st.session_state.inventory_table))


# -----------------------------------------------------------------------------
# Now some cool charts

# Add some space
#''
#''
# #''

# st.subheader('Units left', divider='red')

# need_to_reorder = df[df['units_left'] < df['reorder_point']].loc[:, 'item_name']

# if len(need_to_reorder) > 0:
#     items = '\n'.join(f'* {name}' for name in need_to_reorder)

#     st.error(f"We're running dangerously low on the items below:\n {items}")

# ''
# ''

# st.altair_chart(
#     # Layer 1: Bar chart.
#     alt.Chart(df)
#         .mark_bar(
#             orient='horizontal',
#         )
#         .encode(
#             x='units_left',
#             y='item_name',
#         )
#     # Layer 2: Chart showing the reorder point.
#     + alt.Chart(df)
#         .mark_point(
#             shape='diamond',
#             filled=True,
#             size=50,
#             color='salmon',
#             opacity=1,
#         )
#         .encode(
#             x='reorder_point',
#             y='item_name',
#         )
#     ,
#     use_container_width=True)

# st.caption('NOTE: The :diamonds: location shows the reorder point.')

# ''
# ''
# ''

# -----------------------------------------------------------------------------

st.subheader('Best sellers', divider='orange')

''
''

# st.altair_chart(alt.Chart(df)
#     .mark_bar(orient='horizontal')
#     .encode(
#         x='units_sold',
#         y=alt.Y('item_name').sort('-x'),
#     ),
#     use_container_width=True)

st.write(df)
