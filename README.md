# bacondegrees

A simple command line tool for finding degrees of Kevin Bacon.

## Usage

You can run this as a module, `python -m bacondegrees`, or just call the cli.py file. `python cli.py`, but what you really want to do is install it, `sudo python setup.py install`. That way your can just run `bacondegrees` from the command line.

## Arguments and Options

For searches, just pass in an actors name in quotes

        bacondegrees 'Brad Pitt'

### Prepare Your Bacon

Not happy with your bacon? All you need is a tar containing json files formatted `film.name`, `cast[].name`.

__--cook__, __-c___

Raw bacon?! Never. You need to cook it so you have some movies to work with. If you do a search before running this, it'll be run then.

        bacondegrees --cook

__--burn__, __-b__

Oh, no! Your bacon's burned. Better replace your data with a new tar.

        bacondegrees --burn ~/overwrite-db.tar.gz

__--flip__, __-f__

That bacon's looking a little crispy. Why don't you update it with some fresh tar?

        bacondegrees --flip ~/update-db.tar.gz

### Eat Your Bacon

If plain old bacon isn\'t good enough.

__--grassfed__, __-g__

Delicious organic bacon with caching to speed up future queries. Recommended by both me and your doctor.

        bacondegrees --grassfed 'joaquin phoenix'

__--swanson__, __-s__

For those who literally want all the possible bacon. This'll take a while.

        bacondegrees --swanson

__--vegan__, __-v__

Find those few people who have nothing to do with bacon.

        bacondegrees --vegan