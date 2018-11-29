# --- TESTING ---
#
# Makefile for the dialect detection experiments
#
# Author: G.J.J. van den Burg
# Date: 2018-08-30
#

DATA_DIR=$(realpath ./data)
DATA_DIR_GITHUB=$(DATA_DIR)/github
DATA_DIR_UKDATA=$(DATA_DIR)/ukdata

SCRIPT_DIR=./scripts
ANALYSIS_DIR=$(SCRIPT_DIR)/analysis
DETECTOR_DIR=$(SCRIPT_DIR)/detection
PREPROCESS_DIR=$(SCRIPT_DIR)/preprocessing

OUT_ANALYSE = ./results/test/analysis
OUT_DETECT = ./results/test/detection
OUT_PREPROCESS = ./results/test/preprocessing

DETECTOR_OPTS=

#####################
#                   #
#       GLOBAL      #
#                   #
#####################

help:
	@echo -e "Please see the README for instructions.\nMain targets are 'output' and 'full'.\n"

all: help

.PHONY: data results \
	$(OUT_DETECT)/out_human_ukdata.json $(OUT_DETECT)/out_human_github.json \
	clean_preprocessing clean_results clean_analysis clean_summaries check_clean

# Detector outputs are precious
# https://www.gnu.org/software/make/manual/html_node/Special-Targets.html
.PRECIOUS: \
	$(OUT_DETECT)/out_sniffer_%.json \
	$(OUT_DETECT)/out_hypoparsr_%.json \
	$(OUT_DETECT)/out_suitability_%.json \
	$(OUT_DETECT)/out_our_score_type_only_%.json \
	$(OUT_DETECT)/out_our_score_pattern_only_%.json \
	$(OUT_DETECT)/out_our_score_full_no_tie_%.json \
	$(OUT_DETECT)/out_our_score_full_%.json \
	$(OUT_DETECT)/out_normal_%.json

#####################
#                   #
#        DATA       #
#                   #
#####################

data-dirs:
	mkdir -p $(DATA_DIR_GITHUB)
	mkdir -p $(DATA_DIR_UKDATA)

data: | data-dirs
	python $(SCRIPT_DIR)/data_download.py -i ./urls_github.json -o $(DATA_DIR)/github
	python $(SCRIPT_DIR)/data_download.py -i ./urls_ukdata.json -o $(DATA_DIR)/ukdata

#####################
#                   #
#        META       #
#                   #
#####################

results: figures tables constants

figures tables constants: summaries

figures: figures_github figures_ukdata \
	$(OUT_ANALYSE)/figures/fail_combined.pdf \
	$(OUT_ANALYSE)/figures/violin_combined.pdf

figures_github: \
	$(OUT_ANALYSE)/figures/accuracy_all_github.pdf \
	$(OUT_ANALYSE)/figures/accuracy_human_github.pdf \
	$(OUT_ANALYSE)/figures/accuracy_normal_github.pdf \
	$(OUT_ANALYSE)/figures/runtime_github.pdf

figures_ukdata: \
	$(OUT_ANALYSE)/figures/accuracy_all_ukdata.pdf \
	$(OUT_ANALYSE)/figures/accuracy_human_ukdata.pdf \
	$(OUT_ANALYSE)/figures/accuracy_normal_ukdata.pdf \
	$(OUT_ANALYSE)/figures/runtime_ukdata.pdf

tables: tables_github tables_ukdata

tables_ukdata: \
	$(OUT_ANALYSE)/tables/accuracy_all_ukdata.tex \
	$(OUT_ANALYSE)/tables/accuracy_human_ukdata.tex \
	$(OUT_ANALYSE)/tables/accuracy_normal_ukdata.tex \
	$(OUT_ANALYSE)/tables/standard_and_messy_ukdata.tex

tables_github: \
	$(OUT_ANALYSE)/tables/accuracy_all_github.tex \
	$(OUT_ANALYSE)/tables/accuracy_human_github.tex \
	$(OUT_ANALYSE)/tables/accuracy_normal_github.tex \
	$(OUT_ANALYSE)/tables/standard_and_messy_github.tex


constants: constants_github constants_ukdata \
	$(OUT_ANALYSE)/constants/AccuracyOverallOurs.tex \
	$(OUT_ANALYSE)/constants/ImprovementOverSniffer.tex \
	$(OUT_ANALYSE)/constants/ImprovementOverSnifferMessy.tex \
	$(OUT_ANALYSE)/constants/ImprovementOverSnifferMessyCeil.tex \
	$(OUT_ANALYSE)/constants/PropFailHypoNoResults.tex \
	$(OUT_ANALYSE)/constants/PropFailHypoTimeout.tex \
	$(OUT_ANALYSE)/constants/PropFailSnifferTimeout.tex \
	$(OUT_ANALYSE)/constants/PropFailSnifferNoResults.tex

constants_ukdata: \
	$(OUT_ANALYSE)/constants/NumDialect_ukdata.tex \
	$(OUT_ANALYSE)/constants/PropFailOurFull_ukdata.tex \
	$(OUT_ANALYSE)/constants/NumFiles_ukdata.tex

constants_github: \
	$(OUT_ANALYSE)/constants/NumDialect_github.tex \
	$(OUT_ANALYSE)/constants/PropFailOurFull_github.tex \
	$(OUT_ANALYSE)/constants/NumFiles_github.tex

summaries: summary_github summary_ukdata

summary_github: $(OUT_ANALYSE)/summary_github.json

summary_ukdata: $(OUT_ANALYSE)/summary_ukdata.json

#####################
#                   #
#      SCRIPTS      #
#                   #
#####################

#####################
#                   #
#    PREPROCESS     #
#                   #
#####################

preprocessing: \
	$(OUT_PREPROCESS)/non_normals_ukdata.txt \
	$(OUT_PREPROCESS)/non_normals_github.txt \
	$(OUT_PREPROCESS)/all_files_ukdata.txt \
	$(OUT_PREPROCESS)/all_files_github.txt

# Next four targets are based on this post: https://www.unix.com/unix-for-advanced-and-expert-users/153724-makefile-head-scratcher-multiple-targets-one-go.html
$(OUT_PREPROCESS)/non_normals_ukdata.txt:
	$(SCRIPT_DIR)/run_normal_detection.py $(DATA_DIR_UKDATA) \
		$(OUT_PREPROCESS)/normals_ukdata.json \
		$(OUT_PREPROCESS)/non_normals_ukdata.txt

$(OUT_PREPROCESS)/normals_ukdata.json:
	$(SCRIPT_DIR)/run_normal_detection.py $(DATA_DIR_UKDATA) \
		$(OUT_PREPROCESS)/normals_ukdata.json \
		$(OUT_PREPROCESS)/non_normals_ukdata.txt

$(OUT_PREPROCESS)/non_normals_github.txt:
	$(SCRIPT_DIR)/run_normal_detection.py $(DATA_DIR_GITHUB) \
		$(OUT_PREPROCESS)/normals_github.json \
		$(OUT_PREPROCESS)/non_normals_github.txt

$(OUT_PREPROCESS)/normals_github.json:
	$(SCRIPT_DIR)/run_normal_detection.py $(DATA_DIR_GITHUB) \
		$(OUT_PREPROCESS)/normals_github.json \
		$(OUT_PREPROCESS)/non_normals_github.txt

$(OUT_PREPROCESS)/all_files_github.txt:
	find $(DATA_DIR_GITHUB) -type f | sort > $@

$(OUT_PREPROCESS)/all_files_ukdata.txt:
	find $(DATA_DIR_UKDATA) -type f | sort > $@


#####################
#                   #
#     DETECTORS     #
#                   #
#####################

# meta targets to run detectors independently on both corpora

sniffer: $(OUT_DETECT)/out_sniffer_ukdata.json $(OUT_DETECT)/out_sniffer_github.json

hypoparsr: $(OUT_DETECT)/out_hypoparsr_ukdata.json $(OUT_DETECT)/out_hypoparsr_github.json

human: $(OUT_DETECT)/out_human_ukdata.json $(OUT_DETECT)/out_human_github.json

suitability: $(OUT_DETECT)/out_suitability_ukdata.json $(OUT_DETECT)/out_suitability_github.json

our_score_type_only: $(OUT_DETECT)/out_our_score_type_only_ukdata.json \
	$(OUT_DETECT)/out_our_score_type_only_github.json

our_score_pattern_only: $(OUT_DETECT)/out_our_score_pattern_only_ukdata.json \
	$(OUT_DETECT)/out_our_score_pattern_only_github.json

our_score_full_no_tie: $(OUT_DETECT)/out_our_score_full_no_tie_ukdata.json \
	$(OUT_DETECT)/out_our_score_full_no_tie_github.json

our_score_full: $(OUT_DETECT)/out_our_score_full_ukdata.json \
	$(OUT_DETECT)/out_our_score_full_github.json

#### Ground truth detection

$(OUT_DETECT)/out_normal_%.json: $(OUT_PREPROCESS)/normals_%.json
	$(SCRIPT_DIR)/run_extract_normal.py $^ $@

$(OUT_DETECT)/out_reference_%.json: $(OUT_DETECT)/out_normal_%.json $(OUT_DETECT)/out_human_%.json
	$(SCRIPT_DIR)/merge_human_normal.py $@ $^

$(OUT_DETECT)/out_human_%.json: $(OUT_PREPROCESS)/non_normals_%.txt
	tmux new '$(SCRIPT_DIR)/run_human.py $< $@ && exit'

### Detectors

$(OUT_DETECT)/out_sniffer_%.json: $(OUT_PREPROCESS)/all_files_%.txt
	python $(SCRIPT_DIR)/run_detector.py sniffer $(DETECTOR_OPTS) $< $@

$(OUT_DETECT)/out_hypoparsr_%.json: $(OUT_PREPROCESS)/all_files_%.txt
	$(SCRIPT_DIR)/run_hypoparsr.sh $< $@

$(OUT_DETECT)/out_row_pattern_%.json: $(OUT_PREPROCESS)/all_files_%.txt
	$(SCRIPT_DIR)/run_detector.py row_pattern $(DETECTOR_OPTS) $< $@

$(OUT_DETECT)/out_suitability_%.json: $(OUT_PREPROCESS)/all_files_%.txt
	$(SCRIPT_DIR)/run_detector.py suitability $(DETECTOR_OPTS) $< $@

$(OUT_DETECT)/out_our_score_type_only_%.json: $(OUT_PREPROCESS)/all_files_%.txt
	$(SCRIPT_DIR)/run_detector.py our_score_type_only $(DETECTOR_OPTS) $< $@

$(OUT_DETECT)/out_our_score_pattern_only_%.json: $(OUT_PREPROCESS)/all_files_%.txt
	$(SCRIPT_DIR)/run_detector.py our_score_pattern_only $(DETECTOR_OPTS) $< $@

$(OUT_DETECT)/out_our_score_full_no_tie_%.json: $(OUT_PREPROCESS)/all_files_%.txt
	$(SCRIPT_DIR)/run_detector.py our_score_full_no_tie $(DETECTOR_OPTS) $< $@

$(OUT_DETECT)/out_our_score_full_%.json: $(OUT_PREPROCESS)/all_files_%.txt
	$(SCRIPT_DIR)/run_detector.py our_score_full $(DETECTOR_OPTS) $< $@

#####################
#                   #
#      ANALYSIS     #
#                   #
#####################

$(OUT_ANALYSE)/summary_%.json: \
	$(OUT_DETECT)/out_reference_%.json \
	$(OUT_DETECT)/out_sniffer_%.json \
	$(OUT_DETECT)/out_hypoparsr_%.json \
	$(OUT_DETECT)/out_suitability_%.json \
	$(OUT_DETECT)/out_our_score_full_%.json \
	$(OUT_DETECT)/out_our_score_full_no_tie_%.json \
	$(OUT_DETECT)/out_our_score_pattern_only_%.json \
	$(OUT_DETECT)/out_our_score_type_only_%.json
	$(SCRIPT_DIR)/analysis_summarise.py -c `echo $@ | sed 's/.*\/summary_\(.*\)\.json/\1/'` \
		-s $@ -r $< -o $(filter-out $<, $^)

###########
# figures #
###########

figure-dir:
	mkdir -p $(OUT_ANALYSE)/figures

$(OUT_ANALYSE)/figures/fail_combined.pdf: $(OUT_ANALYSE)/summary_github.json $(OUT_ANALYSE)/summary_ukdata.json | figure-dir
	$(SCRIPT_DIR)/analysis_results.py fail_figure -o $@ -s $^

$(OUT_ANALYSE)/figures/accuracy_all_%.pdf: $(OUT_ANALYSE)/summary_%.json | figure-dir
	$(SCRIPT_DIR)/analysis_results.py accuracy_bar all -o $@ -s $^

$(OUT_ANALYSE)/figures/accuracy_human_%.pdf: $(OUT_ANALYSE)/summary_%.json | figure-dir
	$(SCRIPT_DIR)/analysis_results.py accuracy_bar human -o $@ -s $^

$(OUT_ANALYSE)/figures/accuracy_normal_%.pdf: $(OUT_ANALYSE)/summary_%.json | figure-dir
	$(SCRIPT_DIR)/analysis_results.py accuracy_bar normal -o $@ -s $^

$(OUT_ANALYSE)/figures/runtime_%.pdf: $(OUT_ANALYSE)/summary_%.json | figure-dir
	$(SCRIPT_DIR)/analysis_results.py boxplot -o $@ -s $^

$(OUT_ANALYSE)/figures/violin_combined.pdf: $(OUT_ANALYSE)/summary_github.json $(OUT_ANALYSE)/summary_ukdata.json | figure-dir
	$(SCRIPT_DIR)/analysis_results.py violins -o $@ -s $^

##########
# tables #
##########

table-dir:
	mkdir -p $(OUT_ANALYSE)/tables

$(OUT_ANALYSE)/tables/accuracy_all_%.tex: $(OUT_ANALYSE)/summary_%.json | table-dir
	$(SCRIPT_DIR)/analysis_results.py tables all -o $@ -s $^

$(OUT_ANALYSE)/tables/accuracy_human_%.tex: $(OUT_ANALYSE)/summary_%.json | table-dir
	$(SCRIPT_DIR)/analysis_results.py tables human -o $@ -s $^

$(OUT_ANALYSE)/tables/accuracy_normal_%.tex: $(OUT_ANALYSE)/summary_%.json | table-dir
	$(SCRIPT_DIR)/analysis_results.py tables normal -o $@ -s $^

$(OUT_ANALYSE)/tables/standard_and_messy_%.tex: $(OUT_ANALYSE)/summary_%.json | table-dir
	$(SCRIPT_DIR)/analysis_results.py std_messy -o $@ -s $^

#############
# constants #
#############

const-dir:
	mkdir -p $(OUT_ANALYSE)/constants

$(OUT_ANALYSE)/constants/NumDialect_%.tex: $(OUT_DETECT)/out_reference_%.json | const-dir
	$(SCRIPT_DIR)/analysis_constants.py n_dialect -r $^ -o $@

$(OUT_ANALYSE)/constants/AccuracyOverallOurs.tex: \
	$(OUT_DETECT)/out_reference_github.json \
	$(OUT_DETECT)/out_reference_ukdata.json \
	$(OUT_DETECT)/out_our_score_full_github.json \
	$(OUT_DETECT)/out_our_score_full_ukdata.json | const-dir
	$(SCRIPT_DIR)/analysis_constants.py accuracy_overall -r $(OUT_DETECT)/out_reference_github.json \
		$(OUT_DETECT)/out_reference_ukdata.json -d $(OUT_DETECT)/out_our_score_full_github.json \
		$(OUT_DETECT)/out_our_score_full_ukdata.json -o $@

$(OUT_ANALYSE)/constants/ImprovementOverSniffer.tex: \
	$(OUT_DETECT)/out_reference_github.json \
	$(OUT_DETECT)/out_reference_ukdata.json \
	$(OUT_DETECT)/out_our_score_full_github.json \
	$(OUT_DETECT)/out_our_score_full_ukdata.json \
	$(OUT_DETECT)/out_sniffer_github.json \
	$(OUT_DETECT)/out_sniffer_ukdata.json | const-dir
	$(SCRIPT_DIR)/analysis_constants.py improve_sniffer \
		-r $(OUT_DETECT)/out_reference_github.json $(OUT_DETECT)/out_reference_ukdata.json \
		-d $(OUT_DETECT)/out_our_score_full_github.json $(OUT_DETECT)/out_our_score_full_ukdata.json \
		-s $(OUT_DETECT)/out_sniffer_github.json $(OUT_DETECT)/out_sniffer_ukdata.json \
		-o $@

$(OUT_ANALYSE)/constants/ImprovementOverSnifferMessy.tex: \
	$(OUT_ANALYSE)/summary_github.json $(OUT_ANALYSE)/summary_ukdata.json | const-dir
	$(SCRIPT_DIR)/analysis_constants.py improve_sniffer_messy -s $^ -o $@

$(OUT_ANALYSE)/constants/ImprovementOverSnifferMessyCeil.tex: \
	$(OUT_ANALYSE)/summary_github.json $(OUT_ANALYSE)/summary_ukdata.json | const-dir
	$(SCRIPT_DIR)/analysis_constants.py improve_sniffer_messy --round-up -s $^ -o $@

$(OUT_ANALYSE)/constants/PropFailHypoNoResults.tex: \
	$(OUT_DETECT)/out_hypoparsr_github.json $(OUT_DETECT)/out_hypoparsr_ukdata.json | const-dir
	$(SCRIPT_DIR)/analysis_constants.py failure -r no_results -d $^ -o $@

$(OUT_ANALYSE)/constants/PropFailHypoTimeout.tex: \
	$(OUT_DETECT)/out_hypoparsr_github.json $(OUT_DETECT)/out_hypoparsr_ukdata.json | const-dir
	$(SCRIPT_DIR)/analysis_constants.py failure -r timeout -d $^ -o $@

$(OUT_ANALYSE)/constants/PropFailSnifferNoResults.tex: \
	$(OUT_DETECT)/out_sniffer_github.json $(OUT_DETECT)/out_sniffer_ukdata.json | const-dir
	$(SCRIPT_DIR)/analysis_constants.py failure -r no_results -d $^ -o $@

$(OUT_ANALYSE)/constants/PropFailSnifferTimeout.tex: \
	$(OUT_DETECT)/out_sniffer_github.json $(OUT_DETECT)/out_sniffer_ukdata.json | const-dir
	$(SCRIPT_DIR)/analysis_constants.py failure -r timeout -d $^ -o $@

$(OUT_ANALYSE)/constants/PropFailOurFull_%.tex: $(OUT_ANALYSE)/summary_%.json | const-dir
	$(SCRIPT_DIR)/analysis_constants.py fail_percentage -d our_score_full -s $^ -o $@

$(OUT_ANALYSE)/constants/NumFiles_%.tex: $(OUT_ANALYSE)/summary_%.json | const-dir
	$(SCRIPT_DIR)/analysis_constants.py n_files -s $^ -o $@

#####################
#                   #
#       CLEAN       #
#                   #
#####################

clean: clean_results clean_preprocessing clean_analysis clean_summaries | check_clean

check_clean:
	@echo -n "Are you sure? [y/N]" && read ans && [ $$ans == y ]

clean_preprocessing: check_clean
	rm -f $(OUT_PREPROCESS)/*.{json,txt}

# delete everything but the 'human' output
clean_results: check_clean
	rm -f \
		$(OUT_DETECT)/out_hypoparsr_*.json \
		$(OUT_DETECT)/out_normal_*.json \
		$(OUT_DETECT)/out_our_score_full_no_tie*.json \
		$(OUT_DETECT)/out_our_score_full_*.json \
		$(OUT_DETECT)/out_our_score_pattern_only_*.json \
		$(OUT_DETECT)/out_our_score_type_only_*.json \
		$(OUT_DETECT)/out_reference_*.json \
		$(OUT_DETECT)/out_sniffer_*.json \
		$(OUT_DETECT)/out_suitability_*.json

clean_analysis: clean_summaries
	rm -f $(OUT_ANALYSE)/figures/*
	rm -f $(OUT_ANALYSE)/tables/*
	rm -f $(OUT_ANALYSE)/constants/*

clean_summaries:
	rm -f $(OUT_ANALYSE)/summary_*.json
