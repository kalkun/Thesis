
import scale_annotator.scale_annotator as scale_annotator
import argparse
from protestDB.cursor import ProtestCursor

def main():
	pc = ProtestCursor()
	annotator = scale_annotator.Annotator("images", pc)


if __name__ == '__main__':
	main()