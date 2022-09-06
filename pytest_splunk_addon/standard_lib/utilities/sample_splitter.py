import xmltodict
import os
import argparse


def split_samples(sample_path, output_dir=None, splitter="sourcetype"):
    """
    Splits events to separate files based on provided field

    Args:
        sample_path: path to file with samples
        output_dir: path to directory where separated files will be stored. Default the same dir as input file
        splitter: depend on what filed samples are split. Default: sourcetype, allowed source and host
    """
    if output_dir is None:
        output_dir = os.path.dirname(sample_path)
    with open(sample_path, "r", encoding="utf-8") as sample_file:
        sample_raw = sample_file.read()
    samples = xmltodict.parse(sample_raw)
    events = (
        samples["device"]["event"]
        if type(samples["device"]["event"]) == list
        else [samples["device"]["event"]]
    )
    separate_events = {}
    for each_event in events:
        if "transport" in each_event.keys() and each_event["transport"].get(
            f"@{splitter}"
        ):
            splitter_name = each_event["transport"].get(f"@{splitter}")
            if splitter_name in separate_events.keys():
                separate_events[splitter_name].append(each_event)
            else:
                separate_events[splitter_name] = [each_event]
        else:
            separate_events["undefined"].append(
                each_event
            ) if "undefined" in separate_events.keys() else separate_events.update(
                undefined=[each_event]
            )
    sample_file_name = os.path.basename(sample_path)
    for splitter_name, events in separate_events.items():
        samples["device"].update(event=events)
        output_file = sample_file_name.split(".")
        output_file.insert(-2, splitter_name)
        output_file_name = ".".join(output_file)
        with open(
            os.path.join(output_dir, output_file_name), "w", encoding="utf-8"
        ) as output_file:
            xmltodict.unparse(samples, output=output_file, pretty=True, indent="  ")


def main():
    parser = argparse.ArgumentParser(
        description="Split events from xml file into separate files for each sourcetype"
    )
    parser.add_argument("file", help="xml file with samples to split")
    parser.add_argument(
        "-o", "--output_dir", default=None, help="output dir for new xmls"
    )
    parser.add_argument(
        "-s",
        "--splitter",
        default="sourcetype",
        help="splitter used to separate events",
    )
    args = parser.parse_args()
    sample_path = args.file
    output_dir = args.output_dir
    splitter = args.splitter
    split_samples(sample_path, output_dir, splitter)


if __name__ == "__main__":
    os.getcwd()
    main()
