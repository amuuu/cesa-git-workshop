#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SourceCodeSniffer: Sniff out dangerous code segments
# Copyright (c) 2017, Austin Scott
#
# Contact information:
# Austin Scott
#

# TODO: Detect when we see a SQL query code in a c# function without the sqlCmd.Parameters. or @parameter names or new SqlParameter


"""
Main application logic and automation functions
"""

__version__ = '0.3'
__lastupdated__ = 'October 31, 2017'

###
# Imports
###
import os
import sys
import time
import re
import ConfigParser
import itertools
from string import Template

sys.path.insert(0, os.path.abspath('..'))

# from clint.textui import puts, progress, puts
BAR_TEMPLATE = '%s[%s%s] %i/%i - %s\r'
MILL_TEMPLATE = '%s %s %i/%i\r'
DOTS_CHAR = '.'
BAR_FILLED_CHAR = '#'
BAR_EMPTY_CHAR = ' '
MILL_CHARS = ['|', '/', '-', '\\']
# How long to wait before recalculating the ETA
ETA_INTERVAL = 1
# How many intervals (excluding the current one) to calculate the simple moving
# average
ETA_SMA_WINDOW = 9
STREAM = sys.stderr


class Bar(object):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.done()
        return False  # we're not suppressing exceptions

    def __init__(self, label='', width=32, hide=None, empty_char=BAR_EMPTY_CHAR,
                 filled_char=BAR_FILLED_CHAR, expected_size=None, every=1):
        self.label = label
        self.width = width
        self.hide = hide
        # Only show bar in terminals by default (better for piping, logging etc.)
        if hide is None:
            try:
                self.hide = not STREAM.isatty()
            except AttributeError:  # output does not support isatty()
                self.hide = True
        self.empty_char = empty_char
        self.filled_char = filled_char
        self.expected_size = expected_size
        self.every = every
        self.start = time.time()
        self.ittimes = []
        self.eta = 0
        self.etadelta = time.time()
        self.etadisp = self.format_time(self.eta)
        self.last_progress = 0
        if (self.expected_size):
            self.show(0)

    def show(self, progress, count=None):
        if count is not None:
            self.expected_size = count
        if self.expected_size is None:
            raise Exception("expected_size not initialized")
        self.last_progress = progress
        if (time.time() - self.etadelta) > ETA_INTERVAL:
            self.etadelta = time.time()
            self.ittimes = \
                self.ittimes[-ETA_SMA_WINDOW:] + \
                [-(self.start - time.time()) / (progress + 1)]
            self.eta = \
                sum(self.ittimes) / float(len(self.ittimes)) * \
                (self.expected_size - progress)
            self.etadisp = self.format_time(self.eta)
        x = int(self.width * progress / self.expected_size)
        if not self.hide:
            if ((progress % self.every) == 0 or  # True every "every" updates
                    (progress == self.expected_size)):  # And when we're done
                STREAM.write(BAR_TEMPLATE % (
                    self.label, self.filled_char * x,
                    self.empty_char * (self.width - x), progress,
                    self.expected_size, self.etadisp))
                STREAM.flush()

    def done(self):
        self.elapsed = time.time() - self.start
        elapsed_disp = self.format_time(self.elapsed)
        if not self.hide:
            # Print completed bar with elapsed time
            STREAM.write(BAR_TEMPLATE % (
                self.label, self.filled_char * self.width,
                self.empty_char * 0, self.last_progress,
                self.expected_size, elapsed_disp))
            STREAM.write('\n')
            STREAM.flush()

    def format_time(self, seconds):
        return time.strftime('%H:%M:%S', time.gmtime(seconds))


class logger:
    DEBUG = False;
    VERBOSE = False;

    @staticmethod
    def debug(msg):
        if logger.DEBUG == True:
            print(msg)

    @staticmethod
    def verbose(msg):
        if logger.VERBOSE == True:
            print(msg)

class Colored:
    @staticmethod
    def redback(printString):
        return "\033[0m\033[37m\033[41m" + printString

    @staticmethod
    def black(printString):
        return '\033[0;30m' + printString

    @staticmethod
    def red(printString):
        return '\033[0;31m' + printString

    @staticmethod
    def green(printString):
        return '\033[0;32m' + printString

    @staticmethod
    def yellow(printString):
        return '\033[0;33m' + printString

    @staticmethod
    def blue(printString):
        return '\033[0;34m' + printString

    @staticmethod
    def magenta(printString):
        return '\033[0;35m' + printString

    @staticmethod
    def cyan(printString):
        return '\033[0;36m' + printString

    @staticmethod
    def white(printString):
        return '\033[0;37m'  + printString

    @staticmethod
    def grey(printString):
        return '\033[0;38m' + printString

    @staticmethod
    def reset(printString):
        # return printString
        return '\033[0;39m' + printString

class tabled:
    @staticmethod
    def column(colText, colWidth):
        if len(colText) < colWidth:
            return colText + (" " * (colWidth - len(colText)))


class consoleOut:
    @staticmethod
    def echoOut(echoText):
        os.system("echo " + echoText)


class SourceCodeSnifferMain:
    def __init__(self, argv):
        self.argv = argv
        self._start_time = time.clock()
        self._task_start_time = time.clock()
        self._column_width = 60
        self._sample_code_lines = 3
        self._config_files = ["Default.ini","ASP.ini", "CSharp.ini", "Java.ini", "VBScript.ini"]
        self._ignore_files = (".html", ".js", "robots.txt")
        self._path_to_scan = "."
        self._html_report_filename = "HTML_REPORT.htm"
        self._checklist_report_filename = "CHECKLIST_REPORT.htm"
        self._summaryReportIssuesByFile = {}
        self._summaryReportHighestRiskLevel = {}
        self._summaryReportSourceCodeReviewCheckList = []
        self._summaryHTMLReport = []
        self._summaryReportTimer = {}
        self._summaryRiskTotal = 0
        self._summaryCount = 0

        # Load HTML Template Data
        self._html_template_report = ""
        self._html_template_header = ""
        self._html_template_footer = ""
        self.loadTemplateData()

        # parse arguments
        self.parse_args()

    def get_version(self):
        return "%s" % (__version__)

    def add_to_summary_report(self, text):
        self._summaryReportIssuesByFile.append(text)

    def print_banner(self):
        """
        Prints banner
        """
        print(Colored.red("  Source Code Sniffer Version: " + __version__ + " Updated: " + __lastupdated__) + (" (-h for help)"))

    def usage(self):
        print "\n- Command Line Usage\n\t``# %.65s [options]``\n" % sys.argv[0]
        print "Options\n-------"
        print "====================== =============================================================="
        print "-c --configFiles        specify the config files (default=" + str(self._config_files) + ")"
        print "                        config files should be comma separated"
        print "-p --pathToScan         specify the path to scan (default=" + str(self._path_to_scan) + ")"
        print "                        use the forward slash / for both *nix and windows paths"
        print "-i --ignoreFiles        specify files to not scan (default=" + str(self._ignore_files) + ")"
        print "                        ignored files and file types should be comma separated "
        print "-v --verbose            verbose mode"
        print "-d --debug              show debug output"
        print "-l --log                output to log file"
        print "====================== =============================================================="
        print "Example:"
        print " python SourceCodeSniffer.py -c ASP.ini,CSharp.ini,Default.ini,VBScript.ini -p c:/testpath/test/ -i .html,robots.txt"
    def parse_args(self):
        import getopt
        try:
            opts, args = getopt.getopt(self.argv, "fhvdnc:p:i:",
                                       ["help"])
        except getopt.GetoptError, err:
            print str(err)
            self.usage()
            return 32

        for o, a in opts:
            if o in ("-v", "--verbose"):
                print "verbose"
                logger.VERBOSE = True
            elif o in ("-d", "--debug"):
                print "debug"
                logger.DEBUG = True
            elif o in ("-c", "--configFiles"):
                self._config_files = a.split(',')
            elif o in ("-i", "--ignoreFiles"):
                self._ignore_files = tuple(a.split(','))
            elif o in ("-h", "--help"):
                self.usage()
                sys.exit(0)
                return 0
            elif o in ("-p", "--pathToScan"):
                self._path_to_scan = a
            else:
                assert False, "unknown option"

    def sourceCodeSniffFolder(self):
        # Generate Validation Data Dumps
        for root, subdirs, files in os.walk(os.path.normpath(self._path_to_scan)):
            logger().verbose('--\nroot = ' + root)
            for subdir in subdirs:
                logger().verbose('\t- subdirectory ' + subdir)
                print Colored.white("Scanning folder: "+subdir)
            for filename in bar(files):
                file_path = os.path.join(root, filename)
                logger().debug('\t- file %s (full path: %s)' % (filename, file_path))
                if not file_path.lower().endswith(self._ignore_files):
                    self.sourceCodeSniffFile(file_path)

    def sourceCodeSniffFile(self, file_path):
        file_report_html = ""
        filename_has_been_shown = False
        self._summaryReportIssuesByFile[file_path] = 0
        self._summaryReportHighestRiskLevel[file_path] = 0
        logger().verbose("\t\t- Sniffing a file: %s" % file_path)
        self._summaryHTMLReport.append("<h1>"+file_path+"</h1>")
        for each_section in self.config.sections():
            logger().verbose("\t\t\t- " + each_section.__str__())
            pattern = re.compile(self.config.get(each_section, 'Regex'), re.IGNORECASE)
            try:
                filetosniff = open(file_path)
            except:
                logger().debug("Error accessing file: "+file_path)
                return
            for line_num, line in enumerate(filetosniff):
                for match in re.finditer(pattern, line):
                    logger().debug('\t-Found %s on line %s: %s' % (self.config.get(each_section, 'Message'), line_num + 1 , match.groups()))
                    logger().verbose(line)

                    self._summaryRiskTotal += int(self.config.get(each_section, 'RiskLevel'))
                    self._summaryCount += 1
                    self._summaryReportSourceCodeReviewCheckList.append(self.config.get(each_section, 'Action'))

                    code_sample = ""
                    #if line_num > self._sample_code_lines:
                    #    for sample in itertools.islice(filetosniff, line_num-self._sample_code_lines, line_num+self._sample_code_lines):
                    #        code_sample += sample
                    #else:
                    #    code_sample = line

                    code_sample = line

                    references = ""
                    ref_list = self.config.get(each_section, 'References').split(",")
                    for ref in ref_list:
                        references += "\t\t\t\t<a href='"+ref+"'>"+ref+"</a><br>\n"

                    template_dict = dict()
                    template_dict["Title"] = self.config.get(each_section, 'Title')
                    template_dict["CWE"] = self.config.get(each_section, 'CWE')
                    template_dict["LineNumber"] = line_num+1
                    template_dict["Confidence"] = self.config.get(each_section, 'Confidence')
                    template_dict["RiskLevel"] = self.config.get(each_section, 'RiskLevel')
                    template_dict["Message"] = self.config.get(each_section, 'Message')
                    template_dict["Action"] = self.config.get(each_section, 'Action')
                    template_dict["CodeSample"] = code_sample
                    template_dict["Explanation"] = self.config.get(each_section, 'Explanation')
                    template_dict["References"] = references

                    file_report_html += Template(self._html_template_report).substitute(template_dict)
                    self._summaryHTMLReport.append(file_report_html)

                    self._summaryReportIssuesByFile[file_path] += 1
                    if self._summaryReportHighestRiskLevel[file_path] < int(self.config.get(each_section, 'RiskLevel')):
                        self._summaryReportHighestRiskLevel[file_path] = int(self.config.get(each_section, 'RiskLevel'))


    ##################################################################################
    # Entry point for command-line execution
    ##################################################################################

    def main(self):
        self.print_banner()
        print(Colored.blue("Using configuration files: " + str(self._config_files)))
        print(Colored.blue("Recursively sniffing path for dangerous code: " + self._path_to_scan))
        #sys.stderr = open("errorlog.txt", 'w')
        # load config
        self.config = ConfigParser.ConfigParser()
        self.config.read(self._config_files)

        self.sourceCodeSniffFolder()

        issueCount = sorted(self._summaryReportIssuesByFile.iteritems(), key=lambda x: int(x[1]))
        highestRiskScore = sorted(self._summaryReportHighestRiskLevel.iteritems(), key=lambda x: int(x[1]))

        # Write HTML Report
        file = open(self._html_report_filename, 'w')
        file.write(self._html_template_header)
        for issue in self._summaryHTMLReport:
            file.write(issue)
        file.write(self._html_template_footer)

        # Write Checklist Report
        file = open(self._checklist_report_filename, 'w')
        for checklist in self._summaryReportSourceCodeReviewCheckList:
            file.write(issue)


        print (Colored.blue("Files sorted by potential risk level:"))
        print "{:<4} {:<70}".format('Risk','File Path')
        for k, v in highestRiskScore:
            if v >= 3: print Colored.red("{:<4} {:<70}".format(v, k))
            elif v == 2: print Colored.yellow("{:<4} {:<70}".format(v, k))
            elif v == 1: print Colored.green("{:<4} {:<70}".format(v, k))
            else: print Colored.blue("{:<4} {:<70}".format(v, k))

        print Colored.blue("")
        print "Files sorted by number of potential issues:"
        print "{:<4} {:<70}".format('Issues','File Path')
        for k, v in issueCount:
            print "{:<4} {:<70}".format(v, k)

        sys.exit(0)
        return 0

    def loadTemplateData(self):
        self._html_template_report = """                    
        <div class='summary-report'>
        	<h3>$Title</h3>
        	<table class='summary-table'>
        		<thead>
        		<th>CWE</th>
        		<th>Line #</th>
        		<th>Confidence</th>
        		<th>Risk Level</th>
        		</thead>
        		<tbody>
        		<tr>
        			<td>$CWE</td>
        			<td>$LineNumber</td>
        			<td>$Confidence</td>
        			<td>$RiskLevel</td>
        		</tr>
        		</tbody>
        	</table>
        </div>
        <tr>
        	<td colspan='10'>
        		<div class='problem-description'>
        			<div class='problem-header'>$Message</div>
        			<div class='problem-list'>
        			    $Action
        			</div>
        		</div>
        	</td>
        </tr>
        <pre>
        $CodeSample
        </pre>
        <table class='features-table'>
        <tbody>
        <tr>
        <tr>
        	<td colspan='10'>
        		<div class='feature-description' id='1'>
        		<span>
        		$Explanation
        		</span>
        		<span>
        		<b><i>References:</b><i>
        		$References
        		</span>
        		</div>
        	</td>
        </tr>
        </table>
        """

        self._html_template_header = """
<html>
<head>
	<meta http-equiv='Content-Type' content='text/html; charset=utf-8'></meta>
	<style>
body {
  font-family: Helvetica, Arial, sans-serif;
  font-weight: 300;
}

h2 {
  font-weight: 400;
}

h3 {
  font-weight: 200;
}

table {
  margin: 5px;
}

div.date-test-ran {
  font-size: small;
  font-style: italic;
}

table.features-table {
  width: 800px;
}

table.summary-table {
  width: 800px;
  text-align: left;
  font-weight: bold;
  font-size: small;
}

table.summary-table th {
  background: lightblue;
  padding: 6px;
}

table.summary-table td {
  background: #E0E0E0;
  padding: 6px;
}

pre.title {
  font-family: inherit;
  font-size: 24px;
  line-height: 28px;
  letter-spacing: -1px;
  color: #333;
}

pre.narrative {
  font-family: inherit;
  font-size: 18px;
  font-style: italic;
  line-height: 23px;
  letter-spacing: -1px;
  color: #333;
}

.feature-description {
  font-size: large;
  background: lightblue;
  padding: 12px;
}

.feature-toc-error {
  color: #F89A4F;
}

.feature-toc-failure {
  color: #FF8080;
}

.feature-toc-ignored {
  color: lightgray;
}

.feature-toc-pass {
  color: green;
}

.feature-description.error {
  background: #F89A4F;
}

.feature-description.failure {
  background: #FF8080;
}

.feature-description.ignored {
  background: lightgray;
}

.feature-description.ignored .reason {
  color: black;
  font-style: italic;
  font-size: small;
}

div.issues {
  margin-top: 6px;
  padding: 10px 5px 5px 5px;
  background-color: lemonchiffon;
  color: black;
  font-weight: 500;
  font-size: small;
  max-width: 50%;
}

div.pending-feature {
  background-color: dodgerblue;
  color: white;
  margin-top: 6px;
  padding: 5px;
  text-align: center;
  font-size: small;
  max-width: 120px;
}

div.problem-description {
  padding: 10px;
  background: pink;
  border-radius: 10px;
}

div.problem-header {
  font-weight: bold;
  color: red;
}

div.problem-list {

}

table.ex-table th {
  background: lightblue;
  padding: 0px 5px 0px 5px;
}

table.ex-table td {
  background: #E0E0E0;
  padding: 0px 5px 0px 5px;
}

table td {
  min-width: 50px;
}

col.block-kind-col {
  width: 70px;
}

span.spec-header {
  font-weight: bold;
}

div.spec-text {
  /*color: green;*/
}

div.spec-status {
  font-style: italic;
}

.ignored {
  color: gray;
}

td.ex-result {
  text-align: center;
  background: white !important;
}

.ex-pass {
  color: darkgreen;
}

.ex-fail {
  color: red;
  font-weight: bold;
}

div.block-kind {
  margin: 2px;
  font-style: italic;
}

div.block-text {

}

pre.block-source {
  background-color: whitesmoke;
  padding: 10px;
}

pre.block-source.error {
  background-color: pink;
  color: red;
  font-weight: bold;
}

pre.block-source.pre-error {
  
}

pre.block-source.before-error {
  margin-bottom: -14px;
}

pre.block-source.after-error {
  color: gray;
  margin-top: -14px;
}

pre.block-source.post-error {
  color: gray;
}

div.footer {
  text-align: center;
  font-size: small;
}
</style>
</head>
<body>
<h1>Source Code Sniffer HTML Report</h1>
<hr></hr>
"""

        self._html_template_footer = """
    </body>
    </html>
"""

def bar(it, label='', width=32, hide=None, empty_char=BAR_EMPTY_CHAR, filled_char=BAR_FILLED_CHAR, expected_size=None,
        every=1):
    """Progress iterator. Wrap your iterables with it."""

    count = len(it) if expected_size is None else expected_size

    with Bar(label=label, width=width, hide=hide, empty_char=BAR_EMPTY_CHAR,
             filled_char=BAR_FILLED_CHAR, expected_size=count, every=every) \
            as bar:
        for i, item in enumerate(it):
            yield item
            bar.show(i + 1)


def main(argv=None):
    sourceCodeSnifferMain = SourceCodeSnifferMain(argv if argv else sys.argv[1:])
    return sourceCodeSnifferMain.main()


if __name__ == "__main__":
    sys.exit(main())
