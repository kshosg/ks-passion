from songspeak.licenses import LicensePolicy, output_terms, parse_license


def test_parse_urls_codes_and_names():
    assert parse_license("http://creativecommons.org/licenses/by-nc/3.0/").code == "CC-BY-NC-3.0"
    assert parse_license("https://creativecommons.org/publicdomain/zero/1.0/").code == "CC0-1.0"
    assert parse_license("http://creativecommons.org/licenses/sampling+/1.0/").attribution
    assert parse_license("CC-BY-SA-4.0").share_alike
    assert parse_license("cc0").code == "CC0-1.0"
    assert parse_license("Attribution").code == "CC-BY-4.0"
    assert parse_license("royalty-free").code == "ROYALTY-FREE"
    assert parse_license("CC-BY-SA-3.0").label == "CC BY-SA 3.0"
    assert parse_license("all rights reserved") is None
    assert parse_license("") is None


def test_policy():
    commercial, personal = LicensePolicy(), LicensePolicy(allow_noncommercial=True)
    nd = parse_license("https://creativecommons.org/licenses/by-nd/4.0/")
    nc = parse_license("CC-BY-NC-3.0")
    assert not commercial.allows(nd) and not personal.allows(nd)  # cutting up = adaptation
    assert not commercial.allows(nc) and personal.allows(nc)
    assert commercial.allows(parse_license("CC-BY-SA-3.0"))
    assert not commercial.allows(None)


def test_output_terms():
    by, sa, ncsa, cc0 = (parse_license(x) for x in ("CC-BY-4.0", "CC-BY-SA-3.0", "CC-BY-NC-SA-3.0", "CC0"))
    assert "No attribution required" in output_terms([cc0]).notice
    assert "including commercially" in output_terms([cc0, by]).notice
    assert output_terms([by, sa]).share_alike == "CC BY-SA 4.0"
    assert output_terms([ncsa]).share_alike == "CC BY-NC-SA 4.0"
    assert output_terms([sa, ncsa]).conflict
