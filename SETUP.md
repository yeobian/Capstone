# Project Setup & Usage Guide

This guide will walk you through setting up and running the Personal Wardrobe Intelligence Platform.

## 1. Environment Setup

It's highly recommended to use a virtual environment to manage project dependencies.

1.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    ```
    This creates a new directory named `venv` in your project folder.

2.  **Activate the Virtual Environment:**
    *   **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    *   **On Windows (Command Prompt):**
        ```bash
        venv\Scripts\activate.bat
        ```
    *   **On Windows (PowerShell):**
        ```bash
        venv\Scripts\Activate.ps1
        ```
    You should see `(venv)` at the beginning of your terminal prompt, indicating the environment is active.

3.  **Install Required Dependencies:**
    With your virtual environment activated, install all necessary libraries:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration (Optional but Recommended):**
    Review and adjust `src/config.py` if your project uses a different number of classes or different class names than the default (Tops, Bottoms, Shoes). This file centralizes key parameters for both training and application.

## 5. Data Preparation

The project expects your dataset to be organized in the `data/raw` folder with the following structure:

```
data/raw/
  train/
    tops/
      img1.jpg
      ...
    bottoms/
    shoes/
  val/
    tops/
    ...
```
*   You can create these directories manually or, for quick model testing, use the `create_dummy.py` script to generate a placeholder model. Note that `create_dummy.py` does NOT generate dummy *image data*; you will need to provide your own images following the specified `data/raw` structure.

    **To generate a dummy model:**
    ```bash
    python create_dummy.py
    ```
    This will create a file named `dummy_model.pth` in the `models/` directory, which can be used to run the Streamlit app without a fully trained model.

## 6. Training the Model

To train the machine learning model, run the training script:

```bash
python src/train.py \
    --data_dir data/raw \
    --epochs 20 \
    --batch_size 32 \
    --num_classes 10 \
    --output_dir models/
```
*   Adjust `--epochs`, `--batch_size`, and `--num_classes` as needed for your specific dataset and training goals.
*   Trained models will be saved to the `models/` directory.

## 7. Running the Streamlit Web Application

Once dependencies are installed and a model is available (either trained by you or a pre-trained one placed in `models/`), you can run the interactive web application:

1.  **Ensure your virtual environment is active.**
2.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```
3.  Your web browser should automatically open to the Streamlit application (usually `http://localhost:8501`). If not, navigate there manually.

## 8. Troubleshooting

*   **"command not found: python" or "command not found: pip":** Ensure Python is installed and added to your system's PATH. If using a virtual environment, ensure it is activated.
*   **"ModuleNotFoundError":** This usually means a dependency is missing. Make sure your virtual environment is activated and you have run `pip install -r requirements.txt`.
*   **Streamlit app not opening:** Check your terminal for error messages. Ensure no other application is using port 8501 (Streamlit's default). You can often specify a different port with `streamlit run app.py --server.port 8888`.
*   **"fatal: destination path 'Capstone' already exists and is not an empty directory":** This error occurs if you try to `git clone` into a directory that already contains content. If you're updating, use `git pull` from inside the directory. If setting up fresh, delete the existing `Capstone` folder (if it's not important) before cloning.

## 9. Code Quality and Formatting with Ruff

This project uses [Ruff](https://beta.ruff.rs/docs/) for code linting and formatting to maintain consistent code style and catch potential issues.

1.  **Install Ruff:**
    Ruff is included in `requirements.txt`. Ensure you have installed it by running:
    ```bash
    pip install -r requirements.txt
    ```
    (with your virtual environment activated).

2.  **Configuration:**
    Ruff's configuration is defined in `pyproject.toml` at the root of the project.

3.  **Usage:**
    *   **Check for Linting Errors (without fixing):**
        ```bash
        ruff check .
        ```
        This command will report any linting violations.

    *   **Automatically Fix Linting Errors:**
        ```bash
        ruff check . --fix
        ```
        This will attempt to automatically fix fixable linting issues.

    *   **Format Code (without checking linting):**
        ```bash
        ruff format .
        ```
        This command will reformat your code according to the style rules defined in `pyproject.toml`.

    *   **Check Formatting (without fixing):**
        ```bash
        ruff format . --check
        ```
        This command will report any formatting inconsistencies without changing files.

    *   **Run Check and Format Together:**
        Often, you'll want to run both checking and formatting.
        ```bash
        ruff check . --fix && ruff format .
        ```
        This first fixes linting errors and then formats the code. You might want to run `ruff check .` again after formatting to catch any new issues introduced or remaining.

## 10. Model Evaluation

This project includes a basic evaluation script and a Jupyter Notebook to help you assess your model's performance.

1.  **Evaluation Script (`src/evaluate.py`):**
    A command-line script for running model evaluation.

    ```bash
    python src/evaluate.py --model_path models/your_trained_model.pt --data_dir data/val/
    ```
    *   **Note:** You will need to customize the `src/evaluate.py` file with your specific model loading and evaluation logic.

2.  **Evaluation Notebook (`notebooks/evaluation.ipynb`):**
    A Jupyter Notebook provides an interactive environment for model evaluation, metric calculation, and visualization (e.g., confusion matrices). This is ideal for detailed analysis and presenting results.

    *   **To run the notebook:**
        1.  Ensure your virtual environment is activated.
        2.  Navigate to the project root: `cd Capstone`
        3.  Start Jupyter Lab/Notebook: `jupyter lab` or `jupyter notebook`
        4.  Open `notebooks/evaluation.ipynb` and follow the instructions within.
    *   **Note:** You will need to populate `notebooks/evaluation.ipynb` with the provided markdown content and adjust the placeholder code for your specific model.
