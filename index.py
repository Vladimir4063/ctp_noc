from flask import Flask, redirect, render_template, request, flash
from database.db import *

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/supplystatus", methods=["GET", "POST"])
def supplystatus():
    if request.method == "POST":
        description = request.form["description"]
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cant = description.strip()
        if cant != "":
            cursor.execute(
                "INSERT INTO ctp_supply_status (description) VALUES (%s)", (description,)
            )
            conexion.commit()
            cursor.execute("SELECT * FROM ctp_supply_status")
            supply_status = cursor.fetchall()
            cursor.close()
            conexion.close()
            return render_template("supply_status.html", supply_status=supply_status)

        else:
            # render seccion
            cursor.execute("SELECT * FROM ctp_supply_status")
            supply_status = cursor.fetchall()
            cursor.close()
            conexion.close()
            flash("Please enter valid characters.")
            return render_template("supply_status.html", supply_status=supply_status)

    else:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM ctp_supply_status")
        supply_status = cursor.fetchall()
        cursor.close()
        conexion.close()
        return render_template("supply_status.html", supply_status=supply_status)

@app.route("/delete_supply_status/<id>", methods=["GET", "POST"])
def delete_supply_status(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM ctp_supply_status WHERE status_id = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return redirect("/supplystatus")

@app.route("/update_supply_status/<id>;<desc>", methods=["GET", "POST"])
def update_supply_status(id, desc):
    if request.method == "POST":
        descripcion_new = request.form['description']
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("UPDATE ctp_supply_status SET description = %s WHERE status_id = %s", (descripcion_new ,id))
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect("/supplystatus")
    else:
        return render_template("update_supply_status.html", desc=desc)
    


@app.route("/categories")
def categories():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM ctp_categories")
    parts_categories = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template("categories.html", parts_categories=parts_categories)

@app.route("/subcategory/<id>;<desc>;<abbre>", methods=["GET", "POST"])
def subcategory(id, desc, abbre):
    if request.method == "POST":
        description = request.form["description"]
        abbreviation = request.form["abbreviation"]

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        desc = description.strip()
        abbre = abbreviation.strip()
        if desc == "" or abbre == "":
            if desc != "":
                if abbre != "":
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
                    flash("Please enter valid characters.")

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
                flash("Please enter valid characters.")

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
            flash("Please enter valid characters.")

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
def update_subcategory(id, subid, desc, abbre):

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
    