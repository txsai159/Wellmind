from dependencies import * 
from flask import Flask
app = Flask(__name__, static_folder='templates/static',static_url_path='/static')
cors = CORS(app, resources={r"*": {"origins": "*"}}, supports_credentials=True)

SECRET_KEY = "mindaid"
app.config['SECRET_KEY'] = '123marutidocksuzuki321'                                            
app.config['MONGO_DBNAME'] = 'MINDTEST'                                        
app.config['MONGO_URI'] = 'mongodb://localhost:27017/MINDTEST'  
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_TOKEN_LOCATION'] = ['headers']    
app.config['JWT_HEADER_NAME'] = 'Authorization'  


save_dir = os.path.join(os.getcwd(), "../../mind-aid-development/src/images/")
save_path = os.path.join(save_dir, "edited_certificate.jpg")


mongo.init_app(app)
jwt = JWTManager(app)

def validate_mobile_number(mobile_number):
    if len(mobile_number) == 10 and mobile_number.isdigit():
        return True
    return False

def authenticate_admin(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('token')
        if not token:
            return jsonify({"message": "Authorization token missing", "success": False}), 200
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            kwargs['admin_data'] = data
            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired", "success": False}), 200
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token", "success": False}), 200
    return wrapper



def generate_alphanumeric_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@app.route('/ModuleFunction', methods=['POST'])
#@jwt_required()
def module_function():
    try:
        data = request.json
        modulename = data.get("modulename")
        #user_id = get_jwt_identity()

        # Check if the module already exists for the user with the same test type
        existing_document = mongo.db.student.find_one({"modulename": modulename,  "testtype": data.get("testtype")})
        if existing_document:
            return {"success": False, "message": "Module already exists for the user"}, 400

        module_data = data.get("moduleData")
        moduletype = data.get("testtype")
        query = {"modulename": modulename}
        total_query = {"modulename": modulename, "testtype": moduletype}
        check_if_existing = mongo.db.student.find_one(query)
        endTime = data.get("endTime")

        # Track the current date only if it's the first time for module1
        if modulename == "module1" and not mongo.db.student.find_one({ "currentDate": {"$exists": True}}):
            currentDate = date.today().strftime("%d-%m-%Y")
            data["currentDate"] = currentDate
        else:
            currentDate = None

        if check_if_existing:
            mongo.db.student.update_many({"modulename": modulename}, {"$set": {"testtype": data.get("testtype"), f"moduleData{moduletype}": module_data, "endTime": endTime}})

            module_index = int(re.search(r'\d+', modulename).group()) - 1

            if data.get("testtype") in ("pretest", "activity"):
                mongo.db.student.update_one({"message.name": modulename}, {"$set": {"message.$.status": "in-progress"}})

            elif data.get("testtype") == "posttest":
                check = mongo.db.student.update_one({"message.name": modulename}, {"$set": {"message.$.status": "completed"}})
                if check.modified_count > 0:
                    current_module_number = int(modulename.replace("module", ""))
                    next_module_number = current_module_number + 1
                    next_module_name = f"module{next_module_number}"
                    next_module_status = mongo.db.student.find_one({"message.name": next_module_name})

                    if next_module_status:
                        mongo.db.student.update_one({"message.name": next_module_name}, {"$set": {"message.$.status": "pending"}})
        else:
            #data["user_id"] = user_id
            online_users = mongo.db.student.insert_many([data])

            if data.get("testtype") not in ("pretest", "activity", "posttest"):
                mongo.db.student.update_one({"message.name": modulename}, {"$set": {"message.$.status": "pending"}})

            if data.get("testtype") in ("pretest", "activity"):
                mongo.db.student.update_one({"message.name": modulename }, {"$set": {"message.$.status": "in-progress"}})

            elif data.get("testtype") == "posttest":
                mongo.db.student.update_one({"message.name": modulename}, {"$set": {"message.$.status": "completed"}})

        return {"success": True}

    except Exception as e:
        return {"success": False, "message": "An error occurred during module_function"}
    
@app.route('/AdminRegister', methods=['POST'])
def admin_register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    mobileno = data.get('mobileno')
    place = data.get('place')

    if not name or not email or not password or not mobileno or not place:
        return jsonify({"message": "All fields are required", "success": False}), 400

    if not validate_mobile_number(mobileno):
        return jsonify({"message": "Invalid mobile number format", "success": False}), 400

    existing_admin = mongo.db.admin.find_one({"email": email})
    if existing_admin:
        return jsonify({"message": "Admin with this email already exists", "success": False}), 400

    hashed_password = password
    admin_data = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "mobileno": mobileno,
        "place": place,
        "approval_status": False  # Initially set to False
    }
    mongo.db.admin.insert_one(admin_data)

    return jsonify({"message": "Admin registered successfully", "success": True}), 201

@app.route('/SuperAdminApproveAdmin', methods=['POST'])
def super_admin_approve_admin():
    data = request.json
    mobile_no = data.get('mobileno')

    # Update the approval status to True for the given mobile number
    result = mongo.db.admin.update_one({"mobileno": mobile_no}, {"$set": {"approval_status": True}})

    if result.modified_count == 1:
        return jsonify({"message": "Admin approved successfully!", "success": True}), 200
    else:
        return jsonify({"message": "Admin not found or already approved.", "success": False}), 200

@app.route('/SuperAdminRemoveAdmin', methods=['POST'])
def super_admin_remove_admin():
    data = request.json
    mobile_no = data.get('mobileno')

    # Update the approval status to False for the given mobile number
    result = mongo.db.admin.update_one({"mobileno": mobile_no}, {"$set": {"approval_status": False}})

    if result.modified_count == 1:
        return jsonify({"message": "Admin removed successfully!", "success": True}), 200
    else:
        return jsonify({"message": "Admin not found or already removed.", "success": False}), 200


@app.route('/SuperAdminGetAdminRegistrations', methods=['GET'])
def super_admin_get_admin_registrations():
    try:
        # Find all admin registrations
        admin_registrations = mongo.db.admin.find({}, {"password": 0})  # Exclude the password field
        
        # Prepare the response
        response = {
            "success": True,
            "admin_registrations": list(admin_registrations)
        }
        return jsonify(parse_json(response))
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# @app.route('/studentlogin', methods=['POST'])
# def student_login():
   
#     data = request.json
#     mobileno = data.get('mobileno')
#     password = data.get('password')
#     student = mongo.db.student.find_one({"mobilenumber": mobileno})
   

#     if not student:
#         return jsonify({"message": "Student not found, please register with this mobile number", "success": False}), 200
#     if password == student['password'] :
#         token =create_access_token(identity=mobileno)
        
#         return jsonify({"message": "Student login successful", "token": token, "success": True}), 200
#     else:
#         return jsonify({"message": "Authentication failed", "success": False}), 200



    ret = {'message': "something went wrong with getting studentlist", "success": False}
    student = list(mongo.db.student.find())
    if len(student) != 0:
        ret['message'] = student
        ret['success'] = True
    else:
        ret['message'] = 'No students are registered.'
    return jsonify(parse_json(ret))

@app.route("/resultscreen", methods=['POST'])
#@jwt_required()
def resultScreen():
    try:

        data = request.json
        selectedModule = data.get("selectedModule")
        index = data.get("moduleNumber")
        #user_id = get_jwt_identity()
        Check_Data_Exists = mongo.db.student.find_one({ "modulename": selectedModule})

        response = {}

        if Check_Data_Exists:
            response["success"] = True
            response["moduleData"] = json_util.dumps(Check_Data_Exists)
        else:
            response["success"] = False
            response["moduleData"] = "This module is not completed"

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"success": False, "error": "An error occurred during the operation"}), 500

@app.route("/all_module_status", methods=['GET'])
#@jwt_required()
def getmodulestatus():
    try:
        #user_id = get_jwt_identity() 
        get_current_module_status = mongo.db.student.find_one({ "allmodulestatus": True})
        
        if not get_current_module_status:

            default_data=[]

            for i in range(4):
                    if(i==0):
                        default_data.append({"status": "pending", "name": f"module{i+1}"})
                    else:
                        default_data.append({"status": "Yet to start", "name": f"module{i+1}"})
          

            mongo.db.student.insert_one({
                #"user_id": user_id,
                "allmodulestatus": True,
                "message": default_data
            })

            get_current_module_status = mongo.db.student.find_one({ "allmodulestatus": True})

        ret = get_current_module_status
        return jsonify(parse_json(ret))

    except Exception as e:
        return {"success": False, "message": "An error occurred during getmodulestatus"}
   

@app.route("/certificate_guideline", methods=['POST'])
@jwt_required()
def cerfiticate_guideline():
    try:
        user_id = get_jwt_identity()
        data = request.json
        guideline = data.get("guideline")
        existing_guideline = mongo.db.student.find_one({
            "user_id":user_id,
            "guideline":guideline
        })
       
        if existing_guideline:
            return{
                "success": True,
                "message": "The data is already existis",
                "data":existing_guideline["guideline"]
            }
     
        mongo.db.student.insert_one({
            "user_id": user_id,
            "guideline":guideline
        })

        return {"success":True,"message":"Yes successfully inserted the data!"}

    except Exception as e:
        return {"success": False, "message": "An error occurred during the API call"}


@app.route('/feedback', methods=['POST'])
@jwt_required()
def feedback():
    try:

        user_id = get_jwt_identity()
        data = request.json

        feedback_txt = data.get("feedback")
        
        mongo.db.student.insert_one({
            "user_id":user_id,
            "feedback":feedback_txt
        })
        
        return {"success": True, "message": "Feedback stored successfully"}
    
    except Exception as e:
        return {"success": False, "message": "An error occurred during getmodulestatus"}
   
@app.route('/cerificate_state_store', methods=['POST'])
@jwt_required()
def cerificate_state_store():
    try:

        user_id = get_jwt_identity()
        data = request.json

        certificate = data.get("certificate_downloaded")
        
        mongo.db.student.insert_one({
            "user_id":user_id,
            "certificate_downloaded":certificate
        })
        
        return {"success": True, "message": "Feedback stored successfully"}
    
    except Exception as e:
        return {"success": False, "message": "An error occurred during getmodulestatus"}
   

@app.route("/studentdetailsforadmin", methods=['GET'])

def getallstudentdetails():
    try:
        get_all_student_details = mongo.db.student.find({"userRegistration":True})
        get_feedback = mongo.db.student.find({"feedback": {"$exists": True}})
        ret = {
            "success":True,
            "student_details": get_all_student_details,
            "feedback":get_feedback
            
        }
        return jsonify(parse_json(ret))
    except:
        return {"success": False, "message": "An error occurred during fetching student details"}
    


@app.route("/eachmoduledetails", methods=['GET'])
def eachmoduledetails():
    try:
        user_ids_present = mongo.db.student.find({},'user_id')
        return user_ids_present
    except:
        return {"success": False, "message": "An error occurred during fetching student module details"}

STATUS_COMPLETED = "completed"
STATUS_IN_PROGRESS = "in-progress"
@app.route("/eachmodulestatus",methods=['POST'])
#@jwt_required()
def eachmodulestatus():
    data = request.json
    modulesname = data.get('modulename')
    modulenumber = data.get('modulenumber')
    #user_id = get_jwt_identity() 
    query = {   "modulename":str( modulesname),}
    result = mongo.db.student.find_one(query)
    if result:
        modulename = result.get("modulename")
        moduleStatus = result.get("testtype")
        ret ={
                "success":True,
                "message":{
                    "modulename":modulename,
                    "modulestatus":{
                        "pretest":STATUS_COMPLETED if moduleStatus in ["pretest", "activity", "posttest"] else STATUS_IN_PROGRESS,
                        "activity":STATUS_COMPLETED if moduleStatus in ["activity", "posttest"] else STATUS_IN_PROGRESS,
                        "posttest": STATUS_COMPLETED if moduleStatus in "posttest" else STATUS_IN_PROGRESS
                    }
                }
            }

    else:
        ret = {
        "success": True,
        "message": {
            "modulename": modulesname,
            "modulestatus": {
	    			"pretest" : "in-progress",
	    			"activity" : "in-progress",
	    			"posttest" : "in-progress"
	    		 }
        }}
       
        
    
    return jsonify(parse_json(ret))
    

@app.route('/edit_certificate', methods=['POST'])
def edit_certificate():
    try:
        data = request.json
        suggested_name = data.get('name')

        certificate_image_path = os.path.join(os.getcwd(), "./CertificateIMG.jpg")
        certificate_image = Image.open(certificate_image_path)

        if certificate_image.mode == 'RGBA':
            certificate_image = certificate_image.convert('RGB')

        draw = ImageDraw.Draw(certificate_image)
        font = ImageFont.truetype("arial.ttf", 180)  
        
        text_bbox = draw.textbbox((0, 0), suggested_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        image_width, image_height = certificate_image.size
        text_x = (image_width - text_width) / 2
        text_y = image_height - text_height - 1150  
        draw.text((text_x, text_y), suggested_name, fill="black", font=font)
        edited_image_path = os.path.join(os.getcwd(), "edited_certificate.jpg")
        certificate_image.save(edited_image_path, format='JPEG')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        certificate_image.save(save_path, format='JPEG')
        img_io = io.BytesIO()
        certificate_image.save(img_io, format='JPEG')
        return jsonify({"success": True, "file_url": "/edited_image.jpg"}), 200
       
        # return jsonify({"success": True, "file_path": save_path}), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred during certificate editing"})
    

@app.route('/ml_trained_model_res', methods=['GET'])
def get_edited_image():
    try:
        edited_image_path = os.path.join(os.getcwd(), "stress_comparison.png")
        return send_file(edited_image_path, mimetype='image/png')
    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred while retrieving the image"}), 500



@app.route('/eachstudentmodulestatus', methods=['POST'])
def eachstudentmodulestatus():
    try:
        data = request.json
        user_id = data.get("user_id") 

        moduleDetails = mongo.db.student.find({"user_id":user_id,"testtype": "posttest"})
        current_date_doc = mongo.db.student.find_one({"user_id": user_id, "currentDate": {"$exists": True}})


        current_date = current_date_doc.get("currentDate") if current_date_doc else None

        # Check if current_date is found
        ret=[]
        for details in moduleDetails:

            modulename = details.get("modulename", 'unknown_module')
            feedback = details.get("feedback")
            current_time = float(details.get("currentTime",0))
            end_time = float(details.get("endTime",0))
            total_time_taken =abs(current_time - end_time)
            seconds = total_time_taken // 1000 
            minutes, seconds = divmod(seconds, 60)
            seconds = round(seconds)
    
            ret.append({
                 modulename: [total_time_taken, {"minute":f"{int(minutes)}","second":f"{seconds:02}"}]
        })


        response_data = {
        "success": True,
        "modules": ret,
        "current_date": current_date  # Single date value
    }
        return jsonify(response_data)

        
    except:
        return {"success":False, "message":"An error occured during fetching module details"}
        

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    
    if path and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory('templates', 'index.html')

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True, port=7700)
