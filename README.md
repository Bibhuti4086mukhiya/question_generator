<img width="1362" height="633" alt="image" src="https://github.com/user-attachments/assets/f2608120-718b-4dc4-bd7b-004a47a3a4a0" />
<img width="1343" height="381" alt="image" src="https://github.com/user-attachments/assets/1009bf96-cdac-4515-9338-a27714261419" />
<img width="561" height="592" alt="image" src="https://github.com/user-attachments/assets/a5f573b5-8673-4229-a472-085b54dec8d6" />
<img width="532" height="422" alt="image" src="https://github.com/user-attachments/assets/7a7665e8-9c71-4e6d-94c8-31ecad97b20f" />
<img width="504" height="536" alt="image" src="https://github.com/user-attachments/assets/12582f1f-b1aa-4fc1-a5e0-d222815c59a7" />



add chapter problem done
have add on add question dropdown 

add question and add cateory is connected

if i added new cateory then shoul be show in question types

## Local Development

1.  **Install uv** (if not already installed):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Run the Application**:
    ```bash
    # This will automatically install dependencies and run the app
    uv run app.py
    ```

## Heroku Deployment

1.  **Prepare Files**:
    Heroku needs `gunicorn` as the web server.

    ```bash
    # Add gunicorn
    uv add gunicorn
    ```

2.  **Deploy Commands**:
    ```bash
    # Login to Heroku CLI
    heroku login

    # Create a new Heroku app
    heroku create

    # Add uv buildpack
    heroku buildpacks:add https://github.com/moneymeets/python-uv-buildpack

    # Add PostgreSQL database
    heroku addons:create heroku-postgresql:hobby-dev

    # Push code to Heroku
    git push heroku main

    # Ensure web dyno is running
    heroku ps:scale web=1

    # Open the app
    heroku open
    ```

    **Troubleshooting**:
    If something goes wrong, check the logs:
    ```bash
    heroku logs --tail
    ```
