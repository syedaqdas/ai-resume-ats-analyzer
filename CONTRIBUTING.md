# Contributing to AI Resume ATS Analyzer

Thank you for your interest in contributing to **AI Resume ATS Analyzer**! We welcome contributions from developers, machine learning engineers, UI designers, and technical writers of all experience levels.

---

## Code of Conduct

We are committed to providing a friendly, safe, and welcoming environment for all contributors. Please treat everyone with respect, kindness, and professionalism.

---

## How Can You Contribute?

You can contribute in several ways:
1. **Reporting Bugs:** Submit an issue with reproduction steps and sample anonymized resumes.
2. **Feature Requests:** Propose new scoring heuristics, visualization options, or export formats.
3. **Enhancing Skills Taxonomy:** Add newly emerging frameworks, tools, or domain-specific taxonomies in `utils/skills_database.py`.
4. **Improving Rewriting Models:** Expand the action verb vocabulary or STAR-method suggestion heuristics in `analyzer/suggestions.py`.
5. **Writing Tests:** Enhance unit and integration test coverage in `tests/`.

---

## Development Setup

### 1. Fork and Clone
```bash
git clone https://github.com/your-username/AI-Resume-ATS-Analyzer.git
cd AI-Resume-ATS-Analyzer
```

### 2. Set Up a Virtual Environment
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```

### 5. Run Automated Tests
```bash
pytest -v
```

---

## Pull Request Guidelines

1. **Branch Naming:** Use clear branch prefixes:
   - `feature/your-feature-name`
   - `fix/bug-description`
   - `docs/update-readme`
2. **Code Quality:**
   - Adhere to PEP 8 style standards.
   - Include type hints for all public functions and methods.
   - Write clear docstrings explaining arguments and returns.
3. **Test Coverage:**
   - Always add or update tests in `tests/` for any new logic.
   - Ensure all existing tests pass with `pytest -v`.
4. **Commit Messages:**
   - Use clear, descriptive commit messages (e.g. `feat: add TF-IDF n-gram keyword weighting`, `fix: handle encrypted PDF stream gracefully`).

---

## License

By contributing to this repository, you agree that your contributions will be licensed under the MIT License.
