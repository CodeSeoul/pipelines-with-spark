FROM localhost:5001/spark:python3.12

ADD --chown=spark:spark . /opt/spark/work-dir/

RUN python3.12 -m pip install . && \
    mv src/pipelines/main.py . && \
    rm -rf pyproject.toml src

CMD ["python3.12", "main.py"]
