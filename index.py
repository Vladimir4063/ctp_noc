from flask import Flask, redirect, render_template, request, flash
from flask_paginate import Pagination
from database.db import *

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route("/")
def home():
    return render_template("index.html")


# suspendedparts
@app.route("/suspendedparts", methods=["GET", "POST"])
def suspendedparts():
    if request.method == "POST":
        vendorno = request.form["vendorno"]
        partno = request.form["partno"]

        print(vendorno, partno)

        if len(vendorno) == 0:
            vendorno = "coalesce"
        if len(partno) == 0:
            partno = "coalesce"

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """SELECT VETOPARTS.VENDORNO,
       VNMAS.VMNAME AS VENDORNAME,
       VETOPARTS.PARTNO,
       INMSTA.IMDSC AS PART_DESCRIPTION,
       VETOPARTS.VETOSTAT AS STATUS
FROM VETOPARTS INNER JOIN VNMAS ON VETOPARTS.VENDORNO = VNMAS.VMVNUM
INNER JOIN INMSTA ON VETOPARTS.PARTNO = INMSTA.IMPTN
WHERE VETOPARTS.VENDORNO = %s AND VETOPARTS.PARTNO = %s""", (vendorno, partno,)
        )
        data_supended = cursor.fetchall()
        cursor.close()
        conexion.close()

        return render_template(
            "suspended_parts/suspendedparts.html", data_supended=data_supended
        )
    else:
        return render_template("suspended_parts/suspendedparts.html")


@app.route("/newsuspendedparts")
def newsuspendedparts():
    return render_template("suspended_parts/newsuspendedparts.html")

@app.route("/delete_suspendedparts", methods=["GET", "POST"])
def delete_suspendedparts():
    return redirect("/suspendedparts")

# change_agent
@app.route("/change_agent", methods=["GET", "POST"])
def change_agent():
    if request.method == "POST":

        product_development = int(request.form.get('product_development', '0'))
        vendor_assigned = int(request.form.get('vendor_assigned', '0'))
        cnt03_from = request.form["cnt03_from"]
        cnt03_to = request.form["cnt03_to"]

        if cnt03_from != cnt03_to:

            if product_development == 1 and vendor_assigned == 1:
                conexion = obtener_conexion()
                cursor = conexion.cursor()
                # USER FROM
                cursor.execute("select ususer from CSUSER where uspurc = %s", (cnt03_from,))
                purnofrom = cursor.fetchone()[0]

                # USER DESTINY
                cursor.execute("select ususer from CSUSER where uspurc = %s", (cnt03_to,))
                purnoto = cursor.fetchone()[0]

                # UPDATES
                # update file projects header
                cursor.execute("update PRDVLH set PRPECH = %s where PRPECH = %s;", (purnoto, purnofrom))
                conexion.commit()

                # update file projects detail
                cursor.execute("update PRDVLD set PRDUSR = %s where PRDUSR = %s;", (purnoto, purnofrom))
                conexion.commit()

                # update vendors
                cursor.execute("update VNMAS set `VM#POY` = %s where `VM#POY` = %s;", (purnoto, purnofrom))
                conexion.commit()
                cursor.close()
                conexion.close()

                flash("Records updated.")
                return redirect("/change_agent")

            elif product_development == 1 and vendor_assigned == 0:
                conexion = obtener_conexion()
                cursor = conexion.cursor()
                # USER FROM
                cursor.execute(
                    "select ususer from CSUSER where uspurc = %s", (cnt03_from,)
                )
                purnofrom = cursor.fetchone()[0]

                # USER DESTINY
                cursor.execute(
                    "select ususer from CSUSER where uspurc = %s", (cnt03_to,)
                )
                purnoto = cursor.fetchone()[0]

                # UPDATES
                # update file projects header
                cursor.execute(
                    "update PRDVLH set PRPECH = %s where PRPECH = %s;",
                    (purnoto, purnofrom),
                )
                conexion.commit()

                # update file projects detail
                cursor.execute(
                    "update PRDVLD set PRDUSR = %s where PRDUSR = %s;",
                    (purnoto, purnofrom),
                )
                conexion.commit()
                cursor.close()
                conexion.close()

                flash("Records updated.")
                return redirect("/change_agent")

            elif product_development == 0 and vendor_assigned == 1:
                conexion = obtener_conexion()
                cursor = conexion.cursor()
                # USER FROM
                cursor.execute(
                    "select ususer from CSUSER where uspurc = %s", (cnt03_from,)
                )
                purnofrom = cursor.fetchone()[0]

                # USER DESTINY
                cursor.execute(
                    "select ususer from CSUSER where uspurc = %s", (cnt03_to,)
                )
                purnoto = cursor.fetchone()[0]

                # UPDATES
                # update vendors
                cursor.execute(
                    "update VNMAS set `VM#POY` = %s where `VM#POY` = %s;",
                    (purnoto, purnofrom,),
                )
                conexion.commit()
                cursor.close()
                conexion.close()

                flash("Records updated.")
                return redirect("/change_agent")

            else:
                flash("Not Changes.")
                return redirect("/change_agent")

        else:
            flash("From and to must be different.")
            return redirect("/change_agent")

    else:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT CNT03,CNTDE1 FROM CNTRLL WHERE CNT01 = '216' and trim(substr(cntde1,43,2)) <> 'N' ORDER BY CNTDE1"
        )
        change_agent = cursor.fetchall()
        cursor.close()
        conexion.close()
        return render_template("change_agent.html", change_agent=change_agent)

@app.route("/non_returnable_parts", methods=["GET", "POST"])
def non_returnable_parts():
    if request.method == "POST":
        part_nro = request.form["part-nro"]
        print(part_nro)
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT imptn FROM INMSTA WHERE trim(imptn) = %s", (part_nro,))
        result = cursor.fetchone()
        if result:
            cursor.execute("SELECT * FROM PARTSNONR WHERE PARTNO = %s", (part_nro,))
            exist = cursor.fetchone()
            if exist == None:
                cursor.execute(
                    "INSERT INTO PARTSNONR (PARTNO) values (%s)", (part_nro,)
                )
                conexion.commit()
                cursor.close()
                conexion.close()
                flash("Part Number Added")
                return redirect("/non_returnable_parts")
            else:
                flash("This Part Number Already Exists.")
                return redirect("/non_returnable_parts")
        else:
            flash("Invalid Part Number: " + part_nro)
            return redirect("/non_returnable_parts")
    else:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # count total
        cursor.execute(
            """SELECT COUNT(*) FROM (
    SELECT PARTNO, IMDSC, IMPC1, IMPC2, IMCATA, IMSBCA,
    (SELECT TRIM(CNTDE1) FROM CNTRLL WHERE CNT01 = '110' AND TRIM(CNT02) = '' AND TRIM(CNT03)= IMPC1) AS MJRDSC,
    (SELECT TRIM(CNTDE1) FROM CNTRLL WHERE CNT01 = '120' AND TRIM(CNT02) = '' AND TRIM(CNT03) = IMPC2) AS MNRDSC,
    (SELECT TRIM(INDESC) FROM INMCAT WHERE TRIM(INCATA) = IMCATA) AS CATDSC,
    (SELECT TRIM(INDESS) FROM INMCAS WHERE TRIM(INSBCA) = IMSBCA) AS SUBDSC
    FROM PARTSNONR
    INNER JOIN INMSTA ON PARTSNONR.PARTNO = INMSTA.IMPTN
) AS total"""
        )

        count = cursor.fetchone()[0]

        # Obtener el número de página actual y la cantidad de resultados por página
        page_num = request.args.get("page", 1, type=int)
        per_page = 15

        # Calcular el índice del primer registro y limitar la consulta a un rango de registros
        start_index = (page_num - 1) * per_page + 1

        querySQL = (
            f"SELECT PARTNO, IMDSC, IMPC1, IMPC2, IMCATA, IMSBCA, (SELECT TRIM(CNTDE1) FROM CNTRLL WHERE CNT01 = '110' AND TRIM(CNT02) = '' AND TRIM(CNT03)= IMPC1) MJRDSC,(SELECT TRIM(CNTDE1) FROM CNTRLL WHERE CNT01 = '120' AND TRIM(CNT02)= '' AND TRIM(CNT03) = IMPC2) MNRDSC, (SELECT TRIM(INDESC) FROM INMCAT WHERE TRIM(INCATA) = IMCATA) CATDSC, (SELECT TRIM(INDESS) FROM INMCAS WHERE TRIM(INSBCA)= IMSBCA) SUBDSC FROM PARTSNONR INNER JOIN INMSTA ON PARTSNONR.PARTNO = INMSTA.IMPTN"
            f" LIMIT {per_page} OFFSET {start_index - 1}"
        )

        cursor.execute(querySQL)
        non_returnable_parts = cursor.fetchall()

        # Calcular el índice del último registro
        end_index = min(start_index + per_page, count)
        # end_index = start_index + per_page - 1
        if end_index > count:
            end_index = count

        # Crear objeto paginable
        pagination = Pagination(
            page=page_num,
            total=count,
            per_page=per_page,
            display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>{count}</strong>",
        )
        conexion.commit()

#         cursor.execute(
#             """SELECT PARTNO, IMDSC, IMPC1, IMPC2, IMCATA, IMSBCA, (SELECT TRIM(CNTDE1) FROM CNTRLL WHERE
# CNT01 = '110' AND TRIM(CNT02) = '' AND TRIM(CNT03)= IMPC1) MJRDSC,(SELECT TRIM(CNTDE1) FROM
# CNTRLL WHERE CNT01 = '120' AND TRIM(CNT02)= '' AND TRIM(CNT03) = IMPC2) MNRDSC, (SELECT TRIM(INDESC)
# FROM INMCAT WHERE TRIM(INCATA) = IMCATA) CATDSC,
# (SELECT TRIM(INDESS) FROM INMCAS WHERE TRIM(INSBCA)= IMSBCA) SUBDSC FROM PARTSNONR INNER JOIN INMSTA ON PARTSNONR.PARTNO = INMSTA.IMPTN"""
#         )
#         non_returnable_parts = cursor.fetchall()
        cursor.close()
        conexion.close()

        return render_template(
            "/non_returnable_parts.html",
            non_returnable_parts=non_returnable_parts, pagination=pagination
        )


@app.route("/delete_non_returnable/<part_no>", methods=["GET", "POST"])
def delete_non_returnable(part_no):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM PARTSNONR WHERE PARTNO = %s", (part_no,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return redirect("/non_returnable_parts")


@app.route("/supplystatus", methods=["GET", "POST"])
def supplystatus():
    if request.method == "POST":
        description = request.form["description"]
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cant = description.strip()
        if cant != "":
            cursor.execute(
                "INSERT INTO ctp_supply_status (description) VALUES (%s)",
                (description,),
            )
            conexion.commit()
            cursor.close()
            conexion.close()
            return redirect("/supplystatus")
        else:
            # render seccion
            flash("Please enter valid characters.")
            return redirect("/supplystatus")
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
        descripcion_new = request.form["description"]
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE ctp_supply_status SET description = %s WHERE status_id = %s",
            (descripcion_new, id),
        )
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
                        (
                            id,
                            description,
                            abbreviation,
                        ),
                    )
                    conexion.commit()

                    # Renderizo nuevamente la pantalla
                    cursor.execute(
                        "SELECT * FROM ctp_subcategories cs WHERE FKCategory = %s",
                        (id,),
                    )
                    filters_list = cursor.fetchall()
                    cursor.close()
                    conexion.close()

                    return render_template(
                        "filters.html",
                        filters_list=filters_list,
                        desc=desc,
                        abbre=abbre,
                    )
                else:
                    flash("Please enter valid characters.")

                    # Renderizo nuevamente la pantalla
                    cursor.execute(
                        "SELECT * FROM ctp_subcategories cs WHERE FKCategory = %s",
                        (id,),
                    )
                    filters_list = cursor.fetchall()
                    cursor.close()
                    conexion.close()

                    return render_template(
                        "filters.html",
                        filters_list=filters_list,
                        desc=desc,
                        abbre=abbre,
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
            (
                description,
                abbreviation,
                subid,
            ),
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
        return render_template("update_subcategory.html", desc=desc, abbre=abbre)


@app.route("/delete_subcategory/<id>;<subid>", methods=["GET", "POST"])
def delete_subcategory(id, subid):

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM ctp_subcategories WHERE SubCatCode = %s", (subid,))
    conexion.commit()

    cursor.execute("SELECT * FROM ctp_subcategories cs WHERE FKCategory = %s", (id,))
    filters_list = cursor.fetchall()
    cursor.close()
    conexion.close()

    return render_template("filters.html", filters_list=filters_list)
