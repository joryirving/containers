FROM debian:sid

ARG TARGETPLATFORM
ARG VERSION

WORKDIR /usr/local/bin
RUN apt update && apt install -y curl unzip libsecret-1-0 jq
RUN curl -LO "https://github.com/bitwarden/clients/releases/download/cli-v{$VERSION}/bw-linux-{$VERSION}.zip" \
&& unzip *.zip && chmod +x ./bw

RUN rm *.zip

COPY entrypoint.sh /

CMD ["/entrypoint.sh"]
