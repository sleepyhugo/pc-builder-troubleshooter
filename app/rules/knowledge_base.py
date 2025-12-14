# knowledge_base.py
# This is the hardware knowledge encoded as rules

DIAGNOSTIC_RULES = [
    {
        "symptom": "no_power",
        "question": "Does the PC show no signs of power at all?",
        "probable_causes": [
            "Power supply failure",
            "Front panel connectors wired incorrectly",
            "Dead motherboard",
            "Faulty power cable or outlet"
        ],
        "next_tests": [
            "Try a known-good power cable",
            "Paperclip test the PSU",
            "Check front panel power switch wiring",
            "Test with a known-good PSU"
        ]
    },
    {
        "symptom": "powers_on_no_display",
        "question": "Does the PC power on but show no display?",
        "probable_causes": [
            "Loose or faulty GPU",
            "RAM not seated correctly",
            "Monitor or cable issue",
            "BIOS needs reset"
        ],
        "next_tests": [
            "Reseat RAM (try one stick)",
            "Reseat GPU or try integrated graphics",
            "Clear CMOS",
            "Try a different display cable or monitor"
        ]
    },
    {
        "symptom": "random_shutdowns",
        "question": "Does the PC randomly shut down under load?",
        "probable_causes": [
            "Overheating CPU",
            "Failing power supply",
            "Incorrect CPU cooler installation",
            "Thermal paste issue"
        ],
        "next_tests": [
            "Monitor CPU temperatures in BIOS",
            "Check CPU cooler mounting pressure",
            "Reapply thermal paste",
            "Test with a higher wattage PSU"
        ]
    }
]
