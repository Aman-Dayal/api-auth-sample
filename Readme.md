<!-- create and activate virtual environment -->
python -m venv myenv && myenv/scripts/activate

<!-- Install necessary dependencies -->
pip install fastapi uvicorn python-dotenv requests

<!-- Run the fastapi application with minimal flags-->
uvicorn app:app --reload

<!-- Voila Your application is ready to be accessed -->
