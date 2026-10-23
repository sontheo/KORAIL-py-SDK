# Legal notice

## Unofficial project and trademarks

This is an unofficial interoperability client. It is not affiliated with, endorsed by, sponsored by or supported by Korea Railroad Corporation (KORAIL). It is not an official API, an authorized app instance or a replacement for official customer support. KORAIL, KTX and other third-party names and marks belong to their respective owners. Names identify the services being discussed; no trademark license or endorsement is claimed. The project banner and route artwork are original project illustrations, not official KORAIL branding.

## Software license and scope

[LICENSE](LICENSE) contains the unmodified Apache License, Version 2.0. The maintainer offers material they have authority to license under that license. This statement does not relicense third-party message text, dependencies, trademarks, accounts, application resources or service-access rights. [NOTICE](NOTICE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) form part of the distribution's attribution record.

Apache-2.0 permits personal, internal and commercial use subject to its terms. This repository adds no noncommercial restriction to that license. The maintainer requests personal, noncommercial use and asks users not to operate paid booking services, ticket resale, bulk seat acquisition or sales of automated service access. This is a nonbinding project preference, not an amendment to the license or a statement that every commercial use is unlawful. See the [Apache licensing FAQ](https://www.apache.org/foundation/license-faq.html#IsItFree).

## Implementation boundary

The code is implemented in `src/korail_api/`, the package's only public namespace. [PROVENANCE.md](PROVENANCE.md) records bundled materials and their origins.

## Redistribution

Comply with the conditions that apply to the materials you distribute. For work covered by Apache-2.0, [Section 4](https://www.apache.org/licenses/LICENSE-2.0#redistribution) includes providing the license, identifying modifications, retaining applicable notices, and reproducing applicable NOTICE attribution in a permitted form. Preserve third-party notices and do not misrepresent authorship or remove notices that remain applicable. Distributing dependency binaries may also require their bundled license and notice files; this repository's direct-dependency summary is not an exhaustive license inventory for every environment.

The wheel and source distribution include this project's license and notices for its bundled data and runtime dependencies. Development observations and performance reports are excluded from those artifacts.

## Vendor message data

`src/korail_api/resources/messages/messages.json` contains text extracted from a local KORAIL application resource identified as version `7.0.10`. This text is third-party material, not maintainer-authored text. The source APK and vendor binaries are not distributed. The recorded resource hash and extraction method identify the data but do not authenticate its delivery origin or establish permission to redistribute it.

**No separate redistribution license or permission for this vendor message text has been established by this project.** The Apache-2.0 grant for maintainer-authored code does not grant rights to this text. Inclusion and attribution are not a rights clearance. Anyone proposing redistribution must assess and establish the rights required for their use. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [PROVENANCE.md](PROVENANCE.md).

## Service access, transactions and personal data

A software license, a published repository or a successful request does not itself authorize access to KORAIL systems. Users must establish the permissions and compliance required by applicable law, service terms and their own circumstances. Do not misuse credentials, access accounts without authorization, disrupt services or evade restrictions that apply to you. Users control their request volumes and account activity.

Reservation, cancellation, payment and refund methods can affect real tickets and money. A timeout or response-decoding error does not establish that a transaction failed. Confirm uncertain outcomes through official channels before retrying. Protect credentials, cookies, tokens, passenger and payment details. Raw responses, including error context, may contain sensitive information; do not publish them without appropriate redaction. Users remain responsible for applicable data-protection requirements and their application's collection, storage and disclosure of information.

Transport fingerprints and fallback diagnostic headers do not prove device identity, registration, integrity, enrollment or authorization. The maintainer provides no service-operator permission, transaction guarantee or commercial support commitment.

## Availability, warranty and liability

The external service can change endpoints, response formats, access policies and availability without notice. This development version has been validated using synthetic offline tests. It does not establish live authentication, queue acceptance, booking success, payment completion or production suitability. Official channels remain the source for confirming travel and transaction status.

The warranty disclaimer and liability provisions of [Apache-2.0 Sections 7 and 8](https://www.apache.org/licenses/LICENSE-2.0) apply subject to applicable law. No promise is made of accuracy, uninterrupted access or fitness for a particular purpose. Nothing here excludes obligations or liabilities that applicable law does not permit to be excluded or modifies Apache-2.0. These notices document the project's position and limits; they are not legal advice or certification of a particular use.
