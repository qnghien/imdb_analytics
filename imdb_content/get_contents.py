from imdb import IMDb
import csv

# Initilize IMDB API
ia = IMDb()

def fetch_movie_content(movie_id):
    try:
        movie = ia.get_movie(movie_id.lstrip('tt'))
        plot = movie.get('plot', 'NA')[0]
        synopsis = movie.get('synopsis', 'NA')[0]

        return {
            'movie_id':movie_id,
            'plot': plot,
            'synopsis': synopsis
        }
    except Exception as e:
        print(f"Error fetching data for {movie_id}: {e}")
        return {
            'movie_id': movie_id,
            'plot': 'Error',
            'synopsis': 'Error'
        }


def process_movie_content_to_csv(input_file, output_file):
    try:
        with open(input_file, 'r', newline = '', encoding = 'utf-8') as infile, \
                open(output_file, 'w', newline = '', encoding = 'utf-8') as outfile:

            reader = csv.DictReader(infile)
            fieldnames = ["movie_id", "plot", "synopsis"]
            writer = csv.DictWriter(outfile, fieldnames = fieldnames)
            writer.writeheader()

            for row in reader:
                movie_id = row["movie_id"]
                print(f"Fetching content for movie_id: {movie_id}")
                content = fetch_movie_content(movie_id)
                writer.writerow(content)
                print(f"Done fetching content for movie_id: {movie_id}")

    except FileNotFoundError as e:
        print(f"File not found in this directory: {input_file}")

    except Exception as e:
        print(f"Other unexpected error: {e}")

if __name__ == "__main__":
    input_file = "../imdbscraper/output/movie_info.csv"
    output_file = "output/content.csv"
    process_movie_content_to_csv(input_file, output_file)

    print(f"Complete movie content processing")
