"""
Skills Database and Taxonomy for AI Resume ATS Analyzer.
Provides domain-categorized skills, aliases, and normalization utilities.
"""

from typing import Dict, List, Set

# Comprehensive taxonomy of skills mapped to categories
SKILLS_TAXONOMY: Dict[str, List[str]] = {
    "Programming Languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "C",
        "Go", "Golang", "Rust", "Ruby", "PHP", "SQL", "R", "Swift",
        "Kotlin", "Scala", "Dart", "Shell", "Bash", "PowerShell", "Perl"
    ],
    "Frontend Development": [
        "React", "React.js", "Angular", "Vue", "Vue.js", "Next.js", "Nuxt.js",
        "HTML", "HTML5", "CSS", "CSS3", "SASS", "SCSS", "Tailwind CSS",
        "Bootstrap", "Redux", "MobX", "Svelte", "jQuery", "Webpack",
        "Vite", "GraphQL Client", "Material UI", "Chakra UI"
    ],
    "Backend Development": [
        "Flask", "Django", "FastAPI", "REST API", "RESTful API", "GraphQL",
        "Node.js", "Express", "Express.js", "Spring Boot", "Spring",
        "ASP.NET", ".NET Core", "Microservices", "Celery", "gRPC",
        "NestJS", "Ruby on Rails", "Laravel", "Koa", "Fastify"
    ],
    "Cloud & DevOps": [
        "AWS", "Amazon Web Services", "Azure", "Microsoft Azure", "GCP",
        "Google Cloud Platform", "Docker", "Kubernetes", "K8s", "Terraform",
        "Ansible", "CI/CD", "Jenkins", "GitHub Actions", "GitLab CI",
        "Linux", "Nginx", "Apache", "Helm", "Prometheus", "Grafana",
        "CloudFormation", "Serverless", "AWS Lambda"
    ],
    "Data Science & AI/ML": [
        "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing",
        "Computer Vision", "Pandas", "NumPy", "Scikit-learn", "TensorFlow",
        "Keras", "PyTorch", "OpenCV", "NLTK", "spaCy", "Transformers",
        "Hugging Face", "LLM", "Large Language Models", "LangChain",
        "Data Analysis", "Data Visualization", "Matplotlib", "Seaborn",
        "Plotly", "SciPy", "XGBoost", "LightGBM", "CatBoost"
    ],
    "Databases": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
        "SQLite", "Oracle", "Microsoft SQL Server", "DynamoDB",
        "Cassandra", "Neo4j", "Firebase", "Snowflake", "BigQuery"
    ],
    "Tools & Methodologies": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence",
        "Agile", "Scrum", "Kanban", "TDD", "Test Driven Development",
        "Unit Testing", "Pytest", "Jest", "CI/CD Pipelines",
        "System Design", "OOP", "Object-Oriented Programming",
        "Design Patterns", "Clean Architecture", "Code Review"
    ]
}

# Skill synonyms and aliases normalized to standard canonical names
SKILL_ALIASES: Dict[str, str] = {
    "golang": "Go",
    "js": "JavaScript",
    "ts": "TypeScript",
    "py": "Python",
    "c sharp": "C#",
    "cpp": "C++",
    "reactjs": "React",
    "react.js": "React",
    "vuejs": "Vue",
    "vue.js": "Vue",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "angularjs": "Angular",
    "angular.js": "Angular",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "expressjs": "Express",
    "express.js": "Express",
    "spring-boot": "Spring Boot",
    "k8s": "Kubernetes",
    "k8": "Kubernetes",
    "amazon web services": "AWS",
    "microsoft azure": "Azure",
    "google cloud platform": "GCP",
    "google cloud": "GCP",
    "scikit learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "tf": "TensorFlow",
    "postgres": "PostgreSQL",
    "mongo": "MongoDB",
    "ms sql": "Microsoft SQL Server",
    "sql server": "Microsoft SQL Server",
    "ml": "Machine Learning",
    "natural language processing": "NLP",
    "llms": "LLM",
    "large language models": "LLM",
    "restful": "REST API",
    "rest api": "REST API",
    "rest apis": "REST API",
    "restful apis": "REST API",
    "ci cd": "CI/CD",
    "ci/cd": "CI/CD",
    "continuous integration": "CI/CD",
    "continuous deployment": "CI/CD",
    "tailwind": "Tailwind CSS",
    "test-driven development": "TDD",
    "object oriented programming": "OOP"
}


def get_all_skills() -> Set[str]:
    """Returns a flat set of all unique canonical skills across all domains."""
    skills = set()
    for category_skills in SKILLS_TAXONOMY.values():
        skills.update(category_skills)
    return skills


def get_skill_categories() -> Dict[str, List[str]]:
    """Returns the full dictionary mapping categories to skill lists."""
    return SKILLS_TAXONOMY


def canonicalize_skill(skill_name: str) -> str:
    """
    Normalizes a skill name using aliases, or returns the original title-cased skill.
    """
    cleaned = skill_name.strip()
    lower_cleaned = cleaned.lower()
    if lower_cleaned in SKILL_ALIASES:
        return SKILL_ALIASES[lower_cleaned]
    # Check if case-insensitive match exists in taxonomy
    for cat, skills in SKILLS_TAXONOMY.items():
        for s in skills:
            if s.lower() == lower_cleaned:
                return s
    return cleaned


def get_skill_category_map() -> Dict[str, str]:
    """
    Returns a dictionary mapping lowercase canonical skill to its category name.
    """
    category_map = {}
    for cat, skills in SKILLS_TAXONOMY.items():
        for s in skills:
            category_map[s.lower()] = cat
    return category_map
