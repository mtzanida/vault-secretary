from common import secretary_path, vault_path


def main() -> None:
    vault = vault_path()
    directories = [
        vault / "Inbox",
        vault / "Briefings",
        vault / "Proposals",
        vault / "AWS" / "Community Builders",
        vault / "AWS" / "Article Ideas",
        secretary_path("cache"),
        secretary_path("backups"),
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Ready: {directory}")


if __name__ == "__main__":
    main()

