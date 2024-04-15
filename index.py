from flask import Flask, render_template, request
from database.db import *

app = Flask(__name__)


@app.route("/")
def home():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM ctp_categories")
    parts_categories = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template("index.html", parts_categories=parts_categories)


@app.route("/subcategory/<id>;<desc>;<abbre>", methods=["GET", "POST"])
def subcategory(id, desc, abbre):
    if request.method == "POST":
        description = request.form["description"]
        abbreviation = request.form["abbreviation"]

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO ctp_subcategories (FKCategory, SubCatDescr, SubCategory) VALUES (%s, %s, %s);",
            (id, description, abbreviation,)
        )
        conexion.commit()

        # Renderizo nuevamente la pantalla 
        cursor.execute(
            "SELECT * FROM ctp_subcategories cs WHERE FKCategory = %s", (id,)
        )
        filters_list = cursor.fetchall()
        cursor.close()
        conexion.close()

        return render_template(
            "filters.html", filters_list=filters_list, desc=desc, abbre=abbre
        )
    else:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT * FROM ctp_subcategories cs WHERE FKCategory = %s", (id,)
        )
        filters_list = cursor.fetchall()
        cursor.close()
        conexion.close()

        return render_template(
            "filters.html", filters_list=filters_list, desc=desc, abbre=abbre
        )

@app.route("/update_subcategory/<id>;<subid>;<desc>;<abbre>", methods=["GET", "POST"])
def add_subcategory(id, subid, desc, abbre):

    if request.method == "POST":
        description = request.form["description"]
        abbreviation = request.form["abbreviation"]

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE ctp_subcategories SET SubCatDescr = %s , SubCategory = %s WHERE SubCatCode = %s",
            (description, abbreviation, subid,)
        )
        conexion.commit()

        # traigo nuevamente la tabla sub
        cursor.execute(
            "SELECT * FROM ctp_subcategories cs WHERE FKCategory = %s", (id,)
        )
        filters_list = cursor.fetchall()
        cursor.close()
        conexion.close()

        return render_template(
            "filters.html", filters_list=filters_list, desc=desc, abbre=abbre
        )

    else:
        print(subid)
        print(desc)
        print(abbre)

        return render_template("update_subcategory.html", desc = desc, abbre = abbre)

@app.route("/delete_subcategory/<id>;<subid>", methods=["GET", "POST"])
def delete_subcategory(id, subid):
    
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "DELETE FROM ctp_subcategories WHERE SubCatCode = %s",
        (subid,)
    )
    conexion.commit()
    
    cursor.execute(
        "SELECT * FROM ctp_subcategories cs WHERE FKCategory = %s", (id,)
    )
    filters_list = cursor.fetchall()
    cursor.close()
    conexion.close()

    return render_template(
        "filters.html", filters_list=filters_list
    )
    

if __name__ == "__main__":
    app.run(debug=True)
