# Install uv first. The course notes mention that network access may be required.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install CrewAI through uv.
uv tool install crewai -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

# Run a CrewAI project from its project terminal.
crewai run
