from collections import defaultdict


class CompanyAggregator:
    """
    Combines information extracted from multiple
    website pages into one company profile.
    """

    def __init__(self):
        self.data = {
            "name": None,
            "website": None,
            "description": None,
            "headquarters": None,
            "locations": [],
            "products": [],
            "services": [],
            "solutions": [],
            "industries": [],
            "emails": [],
            "phones": [],
            "address": None,
            "contact_page": None,
            "social_profiles": [],
        }

        # Keep track of where each field came from.
        self.sources = defaultdict(list)

    def _add_unique(
        self,
        field: str,
        value,
        source_url: str | None = None,
    ):
        """
        Add a value to a list field while preventing
        duplicates.
        """

        if value is None:
            return

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return

        if value not in self.data[field]:
            self.data[field].append(value)

        if source_url:
            if source_url not in self.sources[field]:
                self.sources[field].append(
                    source_url
                )

    def _set_if_missing(
        self,
        field: str,
        value,
        source_url: str | None = None,
    ):
        """
        Set a scalar field only when it doesn't already
        contain a value.

        This prevents a weaker later page from
        unnecessarily overwriting an existing value.
        """

        if value is None:
            return

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return

        if self.data[field] is None:
            self.data[field] = value

            if source_url:
                self.sources[field].append(
                    source_url
                )

    def add_page_data(
        self,
        page_data: dict,
        source_url: str | None = None,
    ):
        """
        Merge information extracted from one page.
        """

        # Scalar fields.
        for field in [
            "name",
            "website",
            "description",
            "headquarters",
            "address",
        ]:
            self._set_if_missing(
                field,
                page_data.get(field),
                source_url,
            )

        # List fields.
        for field in [
            "locations",
            "products",
            "services",
            "solutions",
            "industries",
            "emails",
            "phones",
        ]:
            values = page_data.get(field, [])

            if isinstance(values, str):
                values = [values]

            for value in values:
                self._add_unique(
                    field,
                    value,
                    source_url,
                )

        # Contact page.
        contact_page = page_data.get(
            "contact_page"
        )

        if contact_page:
            self._set_if_missing(
                "contact_page",
                contact_page,
                source_url,
            )

        # Social profiles.
        profiles = page_data.get(
            "social_profiles",
            [],
        )

        for profile in profiles:

            if profile not in self.data[
                "social_profiles"
            ]:
                self.data[
                    "social_profiles"
                ].append(profile)

        return self.data

    def result(self) -> dict:
        """
        Return the final aggregated company data.
        """

        return self.data

    def source_map(self) -> dict:
        """
        Return information about where scalar
        fields were obtained from.
        """

        return dict(self.sources)