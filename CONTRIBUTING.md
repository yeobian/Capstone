# Contributing to Capstone Project

We welcome contributions to the Personal Wardrobe Intelligence Platform! Whether it's reporting bugs, suggesting new features, improving documentation, or submitting code changes, your help is valuable.

Please read this guide to understand how you can contribute.

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project, you agree to abide by its terms. (You can link to a CODE_OF_CONDUCT.md file if you create one).

## How Can I Contribute?

### Report Bugs

*   If you find a bug, please check the [issues page](https://github.com/yeobian/Capstone/issues) to see if it has already been reported.
*   If not, open a new issue.
*   When reporting a bug, please include:
    *   A clear and concise description of the bug.
    *   Steps to reproduce the behavior.
    *   Expected behavior.
    *   Screenshots (if applicable).
    *   Your environment details (OS, Python version, dependencies, etc.).

### Suggest Enhancements

*   If you have an idea for a new feature or an improvement, please open an issue on the [issues page](https://github.com/yeobian/Capstone/issues).
*   Clearly describe the enhancement and why you think it would be beneficial.

### Contribute Code

1.  **Fork the Repository:** Start by forking the `yeobian/Capstone` repository to your GitHub account.
2.  **Clone Your Fork:** Clone your forked repository to your local machine.
    ```bash
    git clone https://github.com/YOUR_GITHUB_USERNAME/Capstone.git
    cd Capstone
    ```
3.  **Create a New Branch:** Create a new branch for your feature or bug fix.
    ```bash
    git checkout -b feature/your-feature-name
    # or
    git checkout -b bugfix/issue-description
    ```
4.  **Set Up Your Environment:** Follow the instructions in `SETUP.md` to set up your development environment.
5.  **Make Your Changes:** Implement your feature or fix the bug.
    *   Ensure your code adheres to the project's style guidelines (use `ruff check . --fix` and `ruff format .`).
    *   Add comments where necessary, especially for complex logic.
    *   Write tests for new features or bug fixes (if applicable).
6.  **Commit Your Changes:** Commit your changes with a clear and descriptive commit message.
    ```bash
    git add .
    git commit -m "feat: Add new feature"
    # or
    git commit -m "fix: Resolve bug in X"
    ```
7.  **Push to Your Fork:** Push your branch to your forked repository on GitHub.
    ```bash
    git push origin feature/your-feature-name
    ```
8.  **Open a Pull Request:**
    *   Go to your forked repository on GitHub and click the "New pull request" button.
    *   Provide a clear title and description for your pull request, referencing any related issues.
    *   Ensure all CI checks pass.

## Style Guidelines

*   **Code Formatting:** We use `ruff format` to ensure consistent code style. Please run `ruff format .` before committing your changes.
*   **Linting:** We use `ruff check` to catch common errors and style issues. Please run `ruff check .` (and `ruff check . --fix`) before committing.
*   **Python Best Practices:** Follow PEP 8 guidelines.
*   **Docstrings:** Provide clear docstrings for functions, classes, and modules where appropriate.

## Questions?

If you have any questions or need assistance, feel free to open an issue or reach out!
