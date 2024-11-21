from flask import Flask,render_template,url_for,request,send_file
from flask_sqlalchemy import SQLAlchemy
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import uuid

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/testdb'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db=SQLAlchemy(app)

class Certificate(db.Model):
    id = db.Column(db.Integer,unique=True,autoincrement=True)
    certificate_id = db.Column(db.String(100), unique=True, nullable=False,primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False) 
    course = db.Column(db.String(100), nullable=False)
    completion_date = db.Column(db.String(50), nullable=False)
    issued_by = db.Column(db.String(100), nullable=False) 
     
if not os.path.exists('certificates'):
    os.makedirs('certificates')

@app.route('/')
def index():
  return render_template('index.html')


@app.route('/generate',methods=['POST'])
def generate_certificate():
   name=request.form['name']
   email=request.form['email']
   course=request.form['course']
   issued_by=request.form['issued']
   completion_date=request.form['completion_date']
   certificate_id = f"{name[:3].upper()}-{course[:3].upper()}-{uuid.uuid4().hex[:6]}"


   

   certificate=Certificate(certificate_id=certificate_id,
    name=name,email=email,course=course,
    issued_by=issued_by,completion_date=completion_date
    )
   db.session.add(certificate)
   db.session.commit()
   
   pdf_path = f'certificates/{certificate_id}.pdf'
   create_certificate_pdf(pdf_path, name, course,completion_date, issued_by, certificate_id)

   return send_file(pdf_path, as_attachment=True)

def create_certificate_pdf(pdf_path, name, course, completion_date, issued_by, certificate_id):
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

   
    background_image = "moew.png"  
    if os.path.exists(background_image):
        c.drawImage(background_image, 0, 0, width=width, height=height)

   
    start_y = height * 0.55

   
    c.setFont("Times-BoldItalic", 18)  
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, start_y - 80, "This is to certify that")

    
    c.setFont("Times-BoldItalic", 24) 
    c.setFillColor(colors.HexColor("#154360"))
    c.drawCentredString(width / 2, start_y - 120, name)

    c.setFont("Times-Roman", 16)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, start_y - 160, "has successfully completed the course")

    c.setFont("Courier-Bold", 18) 
    c.setFillColor(colors.HexColor("#2874A6"))
    c.drawCentredString(width / 2, start_y - 200, course)

    c.setFont("Times-Roman", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, start_y - 240, f"Date: {completion_date}")

    c.setFont("Times-Italic", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, start_y - 280, f"Issued by: {issued_by}")

   
    c.setFont("Courier-Bold", 10)  
    c.setFillColor(colors.HexColor("#7D3C98"))
    c.drawCentredString(width / 2, start_y - 320, f"Certificate ID: {certificate_id}")

    c.showPage()
    c.save()
    


@app.route('/verify', methods=['GET', 'POST'])
def verify_certificate():
   if request.method == 'GET':
       return render_template('verify.html')
   if request.method == 'POST':
       certificate_id = request.form['certificate_id']
       cert = Certificate.query.filter_by(certificate_id=certificate_id).first()
       if not cert:
        return render_template('result.html', error="Certificate not found.")
       return render_template('result.html', certificate=cert)



with app.app_context():
    db.create_all()
if __name__ == "__main__":
  app.run(debug=True)

