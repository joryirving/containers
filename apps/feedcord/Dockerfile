FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build

ARG VERSION
ARG CHANNEL
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.joryirving.image.target_platform=$TARGETPLATFORM
LABEL dev.joryirving.image.target_architecture=$TARGETARCH
LABEL dev.joryirving.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/Qolors/FeedCord"

WORKDIR /src

RUN wget https://github.com/Qolors/FeedCord/archive/refs/tags/v${VERSION}.tar.gz \
    && tar -xvf v${VERSION}.tar.gz \
    && cp FeedCord-${VERSION}/FeedCord/FeedCord.csproj ./ \
    && cp -r FeedCord-${VERSION}/FeedCord/src ./src \
    && rm -rf v${VERSION}.tar.gz FeedCord-${VERSION}

RUN dotnet clean \
  && dotnet restore \
  && dotnet build -c Release -o /app/build \
  && dotnet publish -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
WORKDIR /app
COPY --from=build /app/publish .

ENTRYPOINT ["dotnet", "FeedCord.dll"]
