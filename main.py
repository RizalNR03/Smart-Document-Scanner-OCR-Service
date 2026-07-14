import os
import json
import time
from flask import Flask, request, jsonify, render_template, send_from_directory
import cv2
from app.pipeline import SmartScannerPipeline

app = Flask(__name__, template_folder='app/templates')
pipeline = SmartScannerPipeline()

os.makedirs("outputs/debug", exist_ok=True)
os.makedirs("outputs/processed", exist_ok=True)
os.makedirs("outputs/json", exist_ok=True)
os.makedirs("dataset", exist_ok=True) 

def numpy_serializer(obj):
    if hasattr(obj, 'item'):
        return obj.item()
    return str(obj)

@app.route('/static_outputs/<path:filename>')
def serve_outputs(filename):
    return send_from_directory('outputs', filename)

@app.route('/', methods=['GET', 'POST'])
def home_and_process():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "File tidak ditemukan", 400
        file = request.files['file']
        if file.filename == '':
            return "Nama file kosong", 400

        base_name = os.path.splitext(file.filename)[0]
        temp_path = os.path.join("outputs", file.filename)
        file.save(temp_path)

        try:
            metadata, debug, edges, enhanced = pipeline.process(temp_path)

            debug_path = f"debug/{base_name}_contour.jpg"
            edges_path = f"debug/{base_name}_edges.jpg"
            enhanced_path = f"processed/{base_name}_enhanced.jpg"

            cv2.imwrite(os.path.join("outputs", debug_path), debug)
            cv2.imwrite(os.path.join("outputs", edges_path), edges)
            cv2.imwrite(os.path.join("outputs", enhanced_path), enhanced)

            with open(os.path.join("outputs/json", f"{base_name}.json"), "w") as f:
                json.dump(metadata, f, indent=4, default=numpy_serializer)

            json_pretty = json.dumps(metadata, indent=4, default=numpy_serializer)

            return render_template('index.html', 
                                   metadata=metadata, 
                                   json_data=json_pretty,
                                   debug_img=debug_path,
                                   edges_img=edges_path,
                                   enhanced_img=enhanced_path,
                                   time=time.time())
        except Exception as e:
            return f"Terjadi kesalahan sistem: {str(e)}", 500
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    return render_template('index.html', metadata=None)

@app.route('/batch')
def run_batch_processing():
    dataset_dir = "dataset"
    output_json_dir = os.path.join("outputs", "json")
    
    os.makedirs(output_json_dir, exist_ok=True)
    os.makedirs(os.path.join("outputs", "debug"), exist_ok=True)
    os.makedirs(os.path.join("outputs", "processed"), exist_ok=True)
    
    if not os.path.exists(dataset_dir):
        return jsonify({"status": "Error", "message": "Folder 'dataset/' tidak ditemukan"}), 404
        
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.jpg', '.png', '.jpeg', '.jpg', '.JPG')
    images = [f for f in os.listdir(dataset_dir) if f.lower().endswith(image_extensions)]
    
    batch_results = []
    
    for img_name in images:
        img_path = os.path.join(dataset_dir, img_name)
        base_name = os.path.splitext(img_name)[0]
        
        try:
            metadata, debug_mat, edges_mat, enhanced_mat = pipeline.process(img_path)
            
            debug_path = f"debug/{base_name}_batch_contour.jpg"
            edges_path = f"debug/{base_name}_batch_edges.jpg"
            enhanced_path = f"processed/{base_name}_batch_enhanced.jpg"
            
            cv2.imwrite(os.path.join("outputs", debug_path), debug_mat)
            cv2.imwrite(os.path.join("outputs", edges_path), edges_mat)
            cv2.imwrite(os.path.join("outputs", enhanced_path), enhanced_mat)
            
            json_filename = f"{base_name}.json"
            json_path = os.path.join(output_json_dir, json_filename)
            with open(json_path, 'w') as jf:
                json.dump(metadata, jf, indent=4, default=numpy_serializer)
                
            batch_results.append({
                "filename": img_name,
                "status": "Sukses",
                "detected": metadata["document_detected"],
                "debug_img": debug_path,
                "edges_img": edges_path,
                "enhanced_img": enhanced_path,
                "fields": metadata["fields"],
                "time": metadata["processing_time_ms"]
            })
            
        except Exception as e:
            batch_results.append({
                "filename": img_name,
                "status": f"Gagal diproses karena: {str(e)}",
                "detected": False,
                "debug_img": "",  
                "edges_img": "",
                "enhanced_img": "",
                "fields": {"name": "-", "company": "-", "email": "-", "phone": "-"},
                "time": 0
            })
            
    return render_template('batch_results.html', results=batch_results, total=len(images), time=time.time())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)