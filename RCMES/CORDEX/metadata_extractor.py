import glob
import os


class MetadataExtractor(object):
    def __init__(self, *paths):
        """Extracts metadata from data filenames.

        Instances of MetadataExtractor are used to extract metadata from
        filenames in bulk. Example usage:
        >>> extractor = MetadataExtractor('/path/to/data')

        Suppose the data in this directory had the following files:
        pr_*.nc, uas_*.nc, vas_*.nc

        All of the metadata lies in the data attribute:
        >>> extractor.data
        [{'filename': /path/to/data/pr_*.nc, 'variable': 'pr'},
         {'filename': /path/to/data/vas_*.nc, 'variable': 'vas'},
         {'filename': /path/to/data/uas_*.nc, 'variable': 'uas'}]

        Results can be narrowed down by specifying values for a field:
        >>> extractor.query(variable='pr')
        [{'filename': /path/to/data/pr_*.nc, 'variable': 'pr'}]

        Finally, metadata from two sets of extractors can be grouped together
        based on common field name as follows:
        >>> extractor.group(extractor2, 'variable')

        This class should only be used as a starting point. We recommend using
        the included obs4MIPSMetadataExtractor and CORDEXMetadataExtractor
        subclasses or creating your own subclass for your usecase.
        """
        self.paths = paths

    @property
    def data(self):
        """
        The extracted metadata for each file, with all fields listed in
        the fields attribute included.
        """
        return self._data

    @property
    def paths(self):
        """
        Search paths containing the dataset files.
        """
        return self._paths

    @paths.setter
    def paths(self, paths):
        """
        Extracts the metadata from scratch when paths are reset.
        """
        self._paths = paths
        self._extract()

    @property
    def fields(self):
        """
        The name of field in the filename, assuming the fully filtered
        filename conforms to the following convention:
        filename = <field[0]>_<field[1]>_..._<field[n]>.nc. Using fewer fields
        than the filename defines is allowed.
        """
        fields = ['variable']
        return fields

    @property
    def files(self):
        """
        List of files (or regular expressions) for each dataset.
        """
        files = []
        for path in self.paths:
            files.extend(glob.glob(os.path.join(path, '*.nc')))
        return list(set(self.get_pattern(fname) for fname in files))

    @property
    def variables(self):
        """
        Get the list of variables included accross all the datasets.
        """
        return self.get_field('variable')

    @property
    def field_filters(self):
        """
        Override this to filter out specific characters contained in a field.
        """
        return dict()

    def query(self, **kwargs):
        """
        Narrow down the list of files by field names.
        """
        fields = kwargs.keys()
        if not set(fields).issubset(set(self.fields)):
            raise ValueError("Invalid fields: {}. Must be subset of: {}"
                             .format(fields, self.fields))
        data = self.data
        for field, value in kwargs.items():
            value = value if isinstance(value, list) else [value]
            data = [meta for meta in data
                    if self._match_filter(meta, field) in value]
        return data

    def group(self, extractor, field):
        """
        Compare the data of this extractor with another extractor instance
        and group each of their metadata together by given field.
        """
        # First we only want to consider values of field which are contained
        # in both extractors
        subset = self.get_field(field)
        other_subset = extractor.get_field(field)
        intersection = list(subset.intersection(other_subset))

        # Next we will group the datasets in each extractor together by common
        # field values
        kwargs = {field: intersection}
        results = self.query(**kwargs)

        groups = []
        for meta in results:
            val = self._match_filter(meta, field)
            kwargs.update({field: val})
            match = extractor.query(**kwargs)
            groups.append((meta, match))

        return groups

    def get_field(self, field):
        """
        Returns only the selected field of the extracted data.
        """
        if field not in self.fields:
            raise ValueError("Invalid field: {}. Must be one of: {}"
                             .format(field, self.fields))
        sub = set(meta[field] for meta in self.data)
        return sub

    def filter_filename(self, fname):
        """
        Applies a filter to each individual filename contained in the _files
        attribute, which is useful if some files within a data set are known
        to not follow conventions, and "fix" them so that they do.
        """
        return os.path.basename(fname)

    def get_pattern(self, fname):
        """
        Used to group multiple file datasets together via regular expresssions.
        The most common convention is to split files by time periods, which
        are generally the last field in a filename.
        """
        base = fname.split('_')
        pattern = '_'.join(base[:len(self.fields)] + ['*.nc'])
        return pattern

    def _match_filter(self, meta, field):
        """
        Filter (ignore) certain character patterns when matching a field.
        """
        val = meta[field]
        if field in self.field_filters:
            for pattern in self.field_filters[field]:
                val = val.replace(pattern, '')
        return val

    def _extract(self):
        """
        Do the actual metadata extraction from the list of filename given
        via filter_filelist(). Additionally, filenames can also be filtered
        via filter_filename() to remove unwanted characters from the extraction.
        """
        self._data = []
        for fname in self.files:
            meta = dict(filename=fname)

            # Perform the actual metadata extraction
            fname = self.filter_filename(fname)
            meta.update(dict(zip(self.fields, fname.split('_')[:-1])))
            self._data.append(meta)


class obs4MIPSMetadataExtractor(MetadataExtractor):
    @property
    def instruments(self):
        """
        Get the list of instruments accross all the datasets.
        """
        return self.get_field('instrument')

    @property
    def fields(self):
        """
        obs4MIPs fields
        """
        fields = ['variable', 'instrument', 'processing_level', 'version']
        return fields

    @property
    def field_filters(self):
        """
        Field filters for CALIPSO
        """
        return dict(variable=['calipso', 'Lidarsr532'])

    def filter_filename(self, fname):
        """
        CALIPSO files have odd naming conventions, so we will use
        a modified version to conform to standard obs4MIPs conventions.
        """
        fname = os.path.basename(fname)
        fname = fname.replace('_obs4MIPs_', '_')
        return fname

    def get_pattern(self, fname):
        """
        Overriden to deal with CALIPSO filenames
        """
        base = fname.split('_')
        offset = -2 if len(base) != 5 else -1
        pattern = '_'.join(base[:offset] + ['*.nc'])
        return pattern


class CORDEXMetadataExtractor(MetadataExtractor):
    @property
    def models(self):
        """
        Get the list of models accross all the datasets.
        """
        return self.get_field('model')

    @property
    def fields(self):
        """
        obs4MIPs fields
        """
        fields = ['variable', 'domain', 'driving_model', 'experiment',
                  'ensemble', 'model', 'version', 'time_step']
        return fields
