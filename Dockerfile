FROM centos:7 as base
WORKDIR /work
COPY docker/setup_base.sh .
RUN sh setup_base.sh && rm -f setup_base.sh

FROM base as builder
COPY . .
RUN sh docker/setup_venv.sh
RUN sh docker/build_wheel.sh

FROM base
COPY --from=builder /venv /venv
COPY --chmod=755 docker/entrypoint.sh /usr/bin/samsara
EXPOSE 2420
ENTRYPOINT ["samsara"]
CMD ["server"]
