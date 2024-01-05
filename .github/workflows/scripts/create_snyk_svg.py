import json


def get_svg_content(vulnerabilities_count, text):
    color = "FF0000" if vulnerabilities_count > 0 else "008000"
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="110" height="20">',
        '    <linearGradient id="b" x2="0" y2="100%">',
        '        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>',
        '        <stop offset="1" stop-opacity=".1"/>',
        "    </linearGradient>",
        '    <mask id="a">',
        '        <rect width="110" height="20" rx="3" fill="#fff"/>',
        "    </mask>",
        '    <g mask="url(#a)">',
        '        <path fill="#555" d="M0 0h90v20H0z"/>',
        f'        <path fill="#{color}" d="M90 0h110v20H90z"/>',
        '        <path fill="url(#b)" d="M0 0h110v20H0z"/>',
        "    </g>",
        '    <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">',
        f'        <text x="45" y="15" fill="#010101" fill-opacity=".3">Snyk {text}</text>',
        f'        <text x="45" y="14">Snyk {text}</text>',
        f'        <text x="100" y="15" fill="#010101" fill-opacity=".3">{vulnerabilities_count}</text>',
        f'        <text x="100" y="14">{vulnerabilities_count}</text>',
        "    </g>",
        "</svg>",
    ]


def save_svg(svg_content, file_name):
    with open(f".snyk_report/{file_name}.svg", "w") as file:
        for line in svg_content:
            file.write(line + "\n")


dependencies_file = open(".snyk_report/snyk_dependencies.json", "r")
dependencies = json.load(dependencies_file)
dependencies_vuln_count = len(dependencies["vulnerabilities"])
save_svg(
    svg_content=get_svg_content(dependencies_vuln_count, "libs"),
    file_name="snyk_dependencies",
)

code_file = open(".snyk_report/snyk_code.json", "r")
code = json.load(code_file)
code_vuln_count = len(code["runs"][0]["results"])
save_svg(
    svg_content=get_svg_content(code_vuln_count, "code"), file_name="snyk_code"
)
