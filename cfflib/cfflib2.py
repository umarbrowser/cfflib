#!/usr/bin/env python

#
# Generated Tue Jan 25 11:45:14 2011 by generateDS.py version 2.3b.
#

### My Imports

import warnings
from util import *

import sys

import cff as supermod

etree_ = None
Verbose_import_ = False
(   XMLParser_import_none, XMLParser_import_lxml,
    XMLParser_import_elementtree
    ) = range(3)
XMLParser_import_library = None
try:
    # lxml
    from lxml import etree as etree_
    XMLParser_import_library = XMLParser_import_lxml
    if Verbose_import_:
        print("running with lxml.etree")
except ImportError:
    try:
        # cElementTree from Python 2.5+
        import xml.etree.cElementTree as etree_
        XMLParser_import_library = XMLParser_import_elementtree
        if Verbose_import_:
            print("running with cElementTree on Python 2.5+")
    except ImportError:
        try:
            # ElementTree from Python 2.5+
            import xml.etree.ElementTree as etree_
            XMLParser_import_library = XMLParser_import_elementtree
            if Verbose_import_:
                print("running with ElementTree on Python 2.5+")
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree_
                XMLParser_import_library = XMLParser_import_elementtree
                if Verbose_import_:
                    print("running with cElementTree")
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree_
                    XMLParser_import_library = XMLParser_import_elementtree
                    if Verbose_import_:
                        print("running with ElementTree")
                except ImportError:
                    raise ImportError("Failed to import ElementTree from any known place")

def parsexml_(*args, **kwargs):
    if (XMLParser_import_library == XMLParser_import_lxml and
        'parser' not in kwargs):
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        kwargs['parser'] = etree_.ETCompatXMLParser()
    doc = etree_.parse(*args, **kwargs)
    return doc

#
# Globals
#

ExternalEncoding = 'ascii'

#
# Data representation classes
#

class Metadata(supermod.Metadata):
    def __init__(self, tag=None, section=None):
        super(Metadata, self).__init__(tag, section, )
        
    def get_as_dictionary(self):
        """Return the metadata as a dictionary"""
        dat = self.get_tag()
        ret = {}
        for ele in dat:
            ret[ele.key] = ele.valueOf_
        return ret
    
    def set_with_dictionary(self, dictionary):
        """Set the metadata with a dictionary"""
        dat = self.get_tag()
        for k in dictionary:
            test = False
            # check if the key already exists
            for ele in dat:
                if ele.key == k:
                    # always change the value to a string
                    ele.valueOf_ = str(dictionary[k])
                    test = True
            if not test:
                self.data.append(data(str(k),str(dictionary[k])))  
                
                
supermod.Metadata.subclass = Metadata

class connectome(supermod.connectome):
    """The connectome object is the main object of this format.
    It contains CMetadata, and it can contain some CData, CNetwork,
    CSurface, CTimeserie, CTrack, CVolume, CScript or CImagestack
    objects that are referred to as CObjects.
    
    It is possible to store to a simple connectome markup .cml file
    with appropriate relative references to the data files, or to a 
    compressed (zipped) connectome file with ending .cff containing all
    source data objects. """
    
    def __init__(self, connectome_meta=None, connectome_network=None, connectome_surface=None, connectome_volume=None, connectome_track=None, connectome_timeserie=None, connectome_data=None, connectome_script=None, connectome_imagestack=None):
        """Create a new connectome object
        
        See also
        --------
        CMetadata, CNetwork, CSurface, CVolume, CTrack, CTimeserie, CData, CScript and CImagestack
    
        """
        super(connectome, self).__init__(connectome_meta, connectome_network, connectome_surface, connectome_volume, connectome_track, connectome_timeserie, connectome_data, connectome_script, connectome_imagestack, )

        # add parent reference to all children
        self._update_parent_reference()
        
        # add some useful attributes to the save functions
        self.iszip = False
        
        # Default CMetadata
        if connectome_meta is None:
            self.connectome_meta = CMetadata()
        
    def get_all(self):
        """ Return all connectome objects as a list
                    
        Examples
        --------
        >>> allcobj = myConnectome.get_all()
        >>> first_ele = allcobj[0]

        """        
        return self.connectome_network + self.connectome_surface + \
                self.connectome_volume + self.connectome_track + \
                self.connectome_timeserie + self.connectome_data + \
                self.connectome_script + self.connectome_imagestack

    
    def get_by_name(self, name):
        """ Return the list of connectome object(s) that have the given name
        
        Parameters
        ----------
        name : string or list of strings
            name(s) of the requested object(s)
            
        Examples
        --------
        >>> myConnectome.get_by_name('my first network')

        """        
        if isinstance(name, list):
            ret = []
            all_cobj = self.get_all()             
            for ele in all_cobj:
                if ele.name in name:
                    ret.append(ele)
            return ret
        else: 
            #n = self.get_normalised_name(name)
            all_cobj = self.get_all()             
            for ele in all_cobj:
                if name == ele.name:
                    return ele
            return None

    def check_file_in_cff(self):
        """Checks if the files described in the meta.cml are contained in the connectome zip file."""  
        
        if not self.iszip:
            return
        
        all_cobj = self.get_all()
        nlist = self._zipfile.namelist()
        
        for ele in all_cobj:
            
            if not ele.src in nlist:
                msg = "Element with name %s and source path %s is not contained in the connectome file." % (ele.name, ele.src)
                raise Exception(msg)
            
    def check_names_unique(self):
        """Checks whether the names are unique."""  
        all_cobj = self.get_all()
        namelist = []
        for ele in all_cobj:
            namelist.append(ele.name)
        
        # check for non uniqueness
        while len(namelist) > 0:
            e = namelist.pop()
            if e in namelist:
                msg = "Element '%s' has a non unique name! Please change the name to make it unique." % e
                raise Exception(msg)
    
    def is_name_unique(self, name):
        """Check if the given name is unique.
        
        Parameters
        ----------
        name : string,
            the name to check if it is unique
            
        See also
        --------
        check_names_unique, connectome
        """
        n = self.get_normalised_name(name)
        all_cobj = self.get_all()
        namelist = []
        for ele in all_cobj:
            namelist.append(self.get_normalised_name(ele.name))
        if n in namelist:
            return False
        else:
            return True
    
    def get_unique_cff_name(self):
        """Return a unique connectome file title"""
        n = self.get_connectome_meta().get_title().valueOf_
        n = n.lower()
        n = n.replace(' ', '_')
        return n
        
    def get_normalised_name(self, name):
        """Return a normalised name, without space and in lower case
        
        Parameters
        ----------
        name : string,
            the name to be normalised
            
        Examples
        --------
        >>> myConnectome.get_unique_cff_name()
            my_first_network
            
        See also
        --------
        connectome
    
        """
        n = name.lower()
        n = n.replace(' ', '_')
        return n

    def _update_parent_reference(self):
        """Updates the parent reference to the connectome file super-object"""

        all_cobj = self.get_all() 
        
        for ele in all_cobj:
            ele.parent_cfile = self

    def to_xml(self):
        from StringIO import StringIO
        re = StringIO()
        re.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        ns = """xmlns="http://www.connectomics.org/cff-2"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xmlns:dcterms="http://purl.org/dc/terms/" """
        self.export(re, 0, name_= "connectome", namespacedef_=ns)
        re.seek(0)
        return re.read()
    
    def close_all(self, save = False):
        """ Close all currently loaded elements, thereby releasing occupied memory 
        
        Parameters
        ----------
        save : bool,
            Save the content before closing.
            
        """

        all_cobj = self.get_all() 
        for ele in all_cobj:
            if hasattr(ele, 'data') and hasattr(ele, 'tmpsrc') and op.exists(ele.tmpsrc):
                if save:
                    ele.save()
                # remove .data and .tmpsrc
                print "Will not remove file %s from file system" % ele.tmpsrc
                print "Remove .data attribute"
                del ele.data
                print "Remove .tmpsrc attribute"
                del ele.tmpsrc
    
    # CMetadata setter
    def set_connectome_meta(self, cmeta):
        """Set the connectome metadata object for this connectome object
        
        Parameters
        ----------
        cmeta : CMetadata
            the connectome metadata to add to the connectome object
             
        """
                
        # Check if the name is set     
        if cmeta.title is None or cmeta.title == '':
            raise Exception('A title is required.')
        
        self.connectome_meta = cmeta
    
    # CNetwork
    def add_connectome_network_from_nxgraph(self, name, nxGraph, dtype='AttributeNetwork', fileformat='NXGPickle'):
        """Add a new CNetwork from the given NetworkX graph object to the connectome.
        
        Parameters
        ----------
        name : string,
            a unique name for the NetworkX graph to add to the connectome object
        nxGraph : NetworkX,
            a NetworkX graph object
        dtype : AttributeNetwork,
            the data type of this CNetwork
        fileformat : NXGPickle,
            the fileformat of the file of this CNetwork
                    
        Examples
        --------
        >>> myConnectome.add_connectome_network_from_nx(myNXGraph,'nxG1')
            
        See also
        --------
        NetworkX, CNetwork.set_with_nxgraph, CNetwork, connectome.add_connectome_network, connectome   
            
        """
        
        # Check if the name is unique
        if not self.is_name_unique(name):
            raise Exception('The name is not unique.')
            
        n = CNetwork(name)
        n.set_with_nxgraph(nxGraph, dtype, fileformat)
        self.add_connectome_network(n)
        # need to update the reference to the parent connectome file
        self._update_parent_reference()
    
    def add_connectome_network_from_graphml(self, name, graphML):
        """Add a new CNetwork from the given GraphML file to the connectome object.
        
        Parameters
        ----------
        name : string,
            the unique name of the new CNetwork
        graphML : GraphML file,
            the filename of the GraphML to add to the connectome.
                    
        Examples
        --------
        >>> myConnectome.add_connectome_network_from_ml('myGraphML.graphml')
            
        See also
        --------
        GraphML, CNetwork.create_from_graphml, CNetwork, connectome.add_connectome_network, connectome
            
        """
        
        # Check if the name is unique
        if not self.is_name_unique(name):
            raise Exception('The name is not unique.')
        
        n = CNetwork.create_from_graphml(nName, graphML)
        self.add_connectome_network(n)      
        # need to update the reference to the parent connectome file
        self._update_parent_reference()

    def add_connectome_script_from_file(self, name, filename, dtype = 'Python', fileformat = 'UTF-8'):
        """ Add a CScript from a file """
        
        if not self.is_name_unique(name):
            raise Exception('The name is not unique.')
        
        s = CScript.create_from_file(name, filename, dtype= dtype, fileformat = dtype)
        self.add_connectome_script(s)
        # need to update the reference to the parent connectome file
        self._update_parent_reference()

        
    def add_connectome_network(self, cnet):
        """Add the given CNetwork to the connectome object.
        
        Parameters
        ----------
        cnet : CNetwork,
            the connectome network to add to the connectome, the CNetwork name have to be unique.
            
        See also
        --------
        CNetwork, connectome
            
        """
              
        # Check if the name is set     
        if cnet.name is None or cnet.name == '':
            raise Exception('A name is required.')
        
        # Check if the name is unique
        if not self.is_name_unique(cnet.name):
            raise Exception('The name is not unique.')
            
        self.connectome_network.append(cnet)
        
        # need to update the reference to the parent connectome file
        self._update_parent_reference()

        
    # CVolume
    def add_connectome_volume(self, cvol):
        """Add the given CVolume to the connectome object.
        
        Parameters
        ----------
        cnet : CVolume,
            the connectome volume to add to the connectome, the CVolume name have to be unique.
            
        See also
        --------
        CVolume, connectome
            
        """
              
        # Check if the name is set     
        if cvol.name is None or cvol.name == '':
            raise Exception('A name is required.')
        
        # Check if the name is unique
        if not self.is_name_unique(cvol.name):
            raise Exception('The name is not unique.')
            
        self.connectome_volume.append(cvol)
        
    # CSurface
    def add_connectome_surface(self, csurf):
        """Add the given CSurface to the connectome object.
        
        Parameters
        ----------
        csurf : CSurface,
            the connectome surface to add to the connectome, the CSurface name have to be unique.
            
        See also
        --------
        CSurface, connectome
            
        """
              
        # Check if the name is set     
        if csurf.name is None or csurf.name == '':
            raise Exception('A name is required.')
        
        # Check if the name is unique
        if not self.is_name_unique(csurf.name):
            raise Exception('The name is not unique.')
        
        self.connectome_surface.append(csurf)
    
supermod.connectome.subclass = connectome
# end class connectome


class CMetadata(supermod.CMetadata):
    """Specific metadata to the connectome. The name is the name of the connectome. 
    The version and the generator are required and are defined by default."""
    def __init__(self, title='myconnectome', generator='cfflib', version="2.0", creator=None, publisher=None, created=None, modified=None, rights=None, license=None, references=None, relation=None, species=None, email=None, metadata=None ):
        """Creates a connectome metadata object, specific metadata to the connectome object.
        
        Parameters
        ----------
        title : string, default: 'myconnectome',
            the name of this connectome 
        version : string, '2.0',  
            the connectome markup version for this connectome file
            
        creator : string, optional ,
            the creator name
        publisher : string, optional,
            the publisher/institution
        created : string, optional,
            the creation date of this connectome
        modified : string, optional,
            the date of important modification to this connectome object
        license : string, optional,
            license information
        rights : string, optional,
            rights information, such as copyright
        reference : string, optional,
            reference
        relation : string, optional,
            relation
        description : string, optional,
            a text description of the connectome
            
        generator : string, 'cfflib',
            software version/converter this file was generated with
        email : string, optional,
            an email of reference (author one)
        species : string, optional,
            the specied of the subject
                        
        DEPRECATED: metadata : dictionary, optional,
            some metadata informations as a dictionary
            
        Notes
        -----
        Most of the metadata fields are defined in the Dublin Core Terms
        http://dublincore.org/documents/dcmi-terms/
        
        """
        super(CMetadata, self).__init__(version, title, creator, publisher, created, modified, rights, license, references, relation, generator, species, email, metadata, )
##
##        super(CMetadata, self).__init__(version,
##                                        title, 
##                                        creator, 
##                                        publisher, 
##                                        created, 
##                                        modified, 
##                                        rights, 
##                                        license, 
##                                        references, 
##                                        relation, 
##                                        generator, 
##                                        species, 
##                                        email, )
#        if not metadata is None:
#            self.update_metadata(metadata)
#        else:
#            self.update_metadata({})

    def get_metadata_as_dict(self): 
        """Return the metadata as a dictionary"""
        if not self.metadata is None:
            return self.metadata.get_as_dictionary()
        else:
            return None
    
    def update_metadata(self, metadata): 
        """Set the metadata with a dictionary"""
        if self.metadata is None:
            self.metadata = Metadata()
        self.metadata.set_with_dictionary(metadata)
        
supermod.CMetadata.subclass = CMetadata
# end class CMetadata



class CBaseClass(object):

    def load(self, custom_loader = None):
        """ Load the element. The loaded object is stored in the data attribute.
        
        Parameters
        ----------
        custom_loader : function, default: None
            Custom loader function that takes connectome element as
            its first argument.
            
        See Also
        --------
        See cfflib.util.load_data for example. """
        
        if not custom_loader is None:
            self.data = custom_loader(self)
        else:
            self.data = load_data(self)
    
    def save(self):
        """ Save a loaded connectome object to a temporary file, return the path """
        rval = save_data(self)
        if not rval == '':
            self.tmpsrc = rval
            print "Updated storage path of file: %s" % rval
        else:
            raise Exception('There is nothing to save.')

    # Metadata
    def get_metadata_as_dict(self): 
        """Return the metadata as a dictionary"""
        if not self.metadata is None:
            return self.metadata.get_as_dictionary()
        else:
            return None
    
    def update_metadata(self, metadata): 
        """Set the metadata with a dictionary"""
        if self.metadata is None:
            self.metadata = Metadata()
        self.metadata.set_with_dictionary(metadata)
        

class CNetwork(supermod.CNetwork, CBaseClass):
    """A connectome network object"""
    
    def __init__(self, name='mynetwork', dtype='AttributeNetwork', fileformat='GraphML', src=None, description=None, metadata=None):
        """Create a new CNetwork object.
        
        Parameters
        ----------
        name : 'mynetwork',
            the network unique name
        dtype : 'AttributeNetwork',
            the data type of the network. It could be: "AttributeNetwork", "DynamicNetwork", "HierarchicalNetwork" or "Other".
        fileformat : 'GraphML',
            the fileformat of the network. It could be: "GEXF", "GraphML", "NXGPickle" or "Other".
        src : string, optional,
            the source file of the network
        description : plaintext, optional,
            a text description of the CNetwork
        metadata : dictionary, optional,
            Metadata dictionary relative to the network
            
        See also
        --------
        Metadata, connectome
    
        """
        super(CNetwork, self).__init__(src, dtype, name, fileformat, metadata, description, )

        
    def get_unique_relpath(self):
        """ Return a unique relative path for this element """
        
        if self.fileformat == 'GraphML':
            fend = '.graphml'
        elif self.fileformat == 'GEXF':
            fend = '.gexf'
        elif self.fileformat == 'NXGPickle':
            fend = '.gpickle'
        elif self.fileformat == 'Other':
            fend = ''
            
        return unify('CNetwork', self.name + fend)
    
    @classmethod
    def create_from_graphml(cls, name, ml_filename):
        """ Return a CNetwork object from a given ml_filename pointint to
        a GraphML file in your file system
        
        Parameters
        ----------
        name : string,
            unique name of the CNetwork
        ml_filename : string,
            filename of the GraphML to load
        
        Returns
        -------
        cnet : CNetwork
        
        """
        
        # Check if the GraphML file exists
        if not os.path.exists(ml_filename):
            raise Exception('Input file not found')
        
        cnet            = CNetwork(name) 
        cnet.tmpsrc     = op.abspath(ml_filename)
        cnet.fileformat = "GraphML"
        cnet.dtype      = "AttributeNetwork"
        cnet.data       = nx.read_graphml(ml_filename)
        cnet.src        = cnet.get_unique_relpath()

        return cnet
    
    def set_with_nxgraph(self, nxGraph, name=None, dtype='AttributeNetwork', fileformat='NXGPickle'):
        """Set the current CNetwork with the given NetworkX graph.

        Set the fileformat to NXGPickle and the dtype to AttributeNetwork.
        Add the NetworkX object to data.
        
        Parameters
        ----------
        nxGraph : NetworkX graph object,
            the NetworkX graph object to add to the current CNetwork.
        name : string, optional,
            the name of the network, it is optional when the CNetwork already have a name
        dtype : AttributeNetwork,
            the data type of this CNetwork
        fileformat : NXGPickle,
            the fileformat of the file of this CNetwork
                                
        See also
        --------
        NetworkX, CNetwork   
        """
        if (self.name is None or self.name == '') and (name is None or name == ''):
            raise Exception('A name has to be given.')
        if name is not None and name != '':
            self.name == name
        self.dtype      = dtype
        self.fileformat = fileformat
        self.data       = nxGraph
        import tempfile
        # create a path to the temporary pickled file
        self.tmpsrc = tempfile.mkstemp(suffix = '.gpickle')[1]
        self.src    = self.get_unique_relpath()
        # save the object for the first time
        self.save()
    
supermod.CNetwork.subclass = CNetwork
# end class CNetwork


class CSurface(supermod.CSurface, CBaseClass):
    """A connectome surface object"""
    
    def __init__(self, name='mysurface', dtype='label', fileformat='gifti', src=None, description=None, metadata=None):
        """
        Create a new CSurface object.
        
        Parameters
        ----------
        name : 'mysurface'
            the unique surface name
        dtype : 'label',
            the type of data that the Gifti file contain. It could be (for Gifti only): 'label', 'surfaceset', 'surfaceset+label' or 'other'.
        fileformat : 'gifti',
            the fileformat of the surface, use default 'gifti' to use the only supported Gifti format by cfflib, use 'Other' for others format and custom support.
        src : string, optional,
            the source file of the surface
        description : string, optional,
            a description of the CSurface
        metadata : Metadata, optional,
            more metadata relative to the surface
            
        See also
        --------
        Metadata, connectome
    
        """
        super(CSurface, self).__init__(src, dtype, name, fileformat, description, metadata, )
        
    def get_unique_relpath(self):
        """ Return a unique relative path for this element """

        if self.fileformat == 'Gifti':
            fend = '.gii'
        elif self.fileformat == 'Other':
            fend = ''
            
        return unify('CSurface', self.name + fend)
    
    # Description object hide as a property
    @property
    def get_description(self):
        if hasattr(self.description, 'valueOf_'):
            return self.description.get_valueOf_()
        else:
            raise Exception('The description has to be set first.')
    def get_description_format(self):
        if hasattr(self.description, 'format'):
            return self.description.format
        else:
            raise Exception('The description has to be set first.')      
    def set_description(self, value):
        self.description = description('plaintext', value)

    
    # Create from a Gifti file
    @classmethod
    def create_from_gifti(cls, name, gii_filename, dtype='label'):
        """ Return a CSurface object from a given gii_filename pointint to
        a Gifti file in your file system
        
        Parameters
        ----------
        name : string,
            unique name of the CSurface
        gii_filename : string,
            filename of the Gifti to load
        dtype : 'label',
            the type of data the Gifti file contains
        
        Returns
        -------
        csurf : CSurface
        
        """
        csurf            = CSurface(name) 
        csurf.tmpsrc     = op.abspath(gii_filename)
        csurf.fileformat = "Gifti"
        csurf.dtype      = dtype
        import nibabel.gifti as nig
        csurf.data       = nig.read(gii_filename)
        csurf.src        = csurf.get_unique_relpath()
        return csurf
    
supermod.CSurface.subclass = CSurface
# end class CSurface


class CVolume(supermod.CVolume, CBaseClass):
    """Connectome volume object"""
    
    def __init__(self, name='myvolume', dtype=None, fileformat='Nifti1', src=None, description=None, metadata=None):
        """Create a new CVolume object.
        
        Parameters
        ----------
        name : 'myvolume',
            the unique name of the volume
        dtype : string, optional,
            the data type of the volume. It could be: 'T1-weighted', 'T2-weighted', 'PD-weighted', 'fMRI', 'MD', 'FA', 'LD', 'TD', 'FLAIR', 'MRA' or 'MRS depending on your dataset.
        fileformat : 'Nifti1',
            the fileformat of the volume. It could be: 'Nifti1', 'ANALYZE', 'DICOM' ... But only 'Nifti1' is supported, its compressed version '.nii.gz' too.
        src : string, optional,
            the source file of the volume
        description : string, optional,
           A description according to the format attribute syntax.
        metadata : Metadata, optional,
            More metadata relative to the volume
                                
        See also
        --------
        Metadata, connectome
        """
        super(CVolume, self).__init__(src, dtype, name, fileformat, description, metadata, )
#        self.src = self.get_unique_relpath()
                  
    def get_unique_relpath(self):
        """ Return a unique relative path for this element """
    
        if self.fileformat == 'Nifti1':
            fend = '.nii.gz'
        elif self.fileformat == 'ANALYZE':
            print "Save ANALYZE file in Nifti format .nii.gz"
            fend = '.nii.gz'
        elif self.fileformat == 'DICOM':
            print "Saving in DICOM format not supported."
            fend = ''
        else:
            fend = ''
            
        return unify('CVolume', self.name + fend)
    
    # Description object hide as a property
    @property
    def get_description(self):
        if hasattr(self.description, 'valueOf_'):
            return self.description.get_valueOf_()
        else:
            raise Exception('The description has to be set first.')
    def get_description_format(self):
        if hasattr(self.description, 'format'):
            return self.description.format
        else:
            raise Exception('The description has to be set first.')    
    def set_description(self, value):
        self.description = description('plaintext', value)
       
    # Create a CVolume from a Nifti1 file
    @classmethod
    def create_from_nifti(cls, name, nii_filename, dtype=None):
        """ Return a CVolume object from a given Nifti1 filename in your file system
        
        Parameters
        ----------
        name : string,
            the unique name of the CVolume
        nii_filename : string,
            the filename of the Nifti1 file to load
        dtype : string, optional,
            the datatype of the new CVolume
        
        Returns
        -------
        cvol : CVolume
        
        """
        cvol            = CVolume(name) 
        cvol.tmpsrc     = op.abspath(nii_filename)
        cvol.fileformat = "Nifti1"
        cvol.dtype      = dtype
        cvol.data       = ni.load(nii_filename)
        cvol.src        = cvol.get_unique_relpath()
        return cvol
    
supermod.CVolume.subclass = CVolume
# end class CVolume

class CTrack(supermod.CTrack, CBaseClass):
    """
        Create a new CTrack object.
        
        Parameters
        ----------
            name              : string, optional
                the track name
            src               : string, optional,
                the source file of the track
            fileformat        : string, optional,
                the fileformat of the track
            description       : description, optional,
                a description (key, value) of the CTrack
            metadata          : Metadata, optional,
                Metadata object relative to the track
                    
        Examples
        --------
            Empty
            >>> myCVol1 = CTrack()
            Create an empty CTrack object
            
        See also
        --------
            description, Metadata, connectome
    
    """
    def __init__(self, name=None, src=None, fileformat='TrackVis', description=None, metadata=None):
        super(CTrack, self).__init__(src, name, fileformat, description, metadata, )
                        
    def get_unique_relpath(self):
        """ Return a unique relative path for this element """
    
        if self.fileformat == 'TrackVis':
            fend = '.trk'
        elif self.fileformat == 'Other':
            fend = ''
            
        return unify('CTrack', self.name + fend)
    
supermod.CTrack.subclass = CTrack
# end class CTrack


class CTimeserie(supermod.CTimeserie, CBaseClass):
    def __init__(self, src=None, name=None, fileformat='HDF5', description=None, metadata=None):
        super(CTimeserie, self).__init__(src, name, fileformat, description, metadata, )
                
    def get_unique_relpath(self):
        """ Return a unique relative path for this element """
        
        if self.fileformat == 'HDF5':
            fend = '.h5'
        elif self.fileformat == 'Other':
            fend = ''
            
        return unify('CTimeserie', self.name + fend)
    
supermod.CTimeserie.subclass = CTimeserie
# end class CTimeserie


class CData(supermod.CData, CBaseClass):
    def __init__(self, src=None, name=None, fileformat=None, description=None, metadata=None):
        super(CData, self).__init__(src, name, fileformat, description, metadata, )
                
    def get_unique_relpath(self):
        """ Return a unique relative path for this element """
        
        if self.fileformat == 'NumPy':
            fend = '.npy'
        if self.fileformat == 'HDF5':
            fend = '.h5'
        if self.fileformat == 'XML':
            fend = '.xml'
        elif self.fileformat == 'Other':
            fend = ''
            
        return unify('CData', self.name + fend)
    
supermod.CData.subclass = CData
# end class CData


class CScript(supermod.CScript, CBaseClass):
    def __init__(self, src=None, dtype='Python', name=None, fileformat='UTF-8', description=None, metadata=None):
        super(CScript, self).__init__(src, dtype, name, fileformat, description, metadata, )
        
    def get_unique_relpath(self):
        """ Return a unique relative path for this element """
        
        if self.dtype == 'Python':
            fend = '.py'
        elif self.dtype == 'Bash':
            fend = '.sh'
        elif self.dtype == 'Matlab':
            fend = '.m'
        else:
            fend = '.txt'
            
        return unify('CScript', self.name + fend)

    @classmethod
    def create_from_file(cls, name, filename, dtype= 'Python', fileformat = 'UTF-8'):
        """ Return a CScript object from a given script/text file
        
        Parameters
        ----------
        name : string,
            the unique name of the CScript
        filename : string,
            the absolute to the filename of the script/text file
        dtype : string, optional,
            the datatype of the new CScript
        fileformat : string, optional
            the file format of the file, usually UTF-8
        
        Returns
        -------
        cscr : CScript
        
        """
        cscr            = CScript(name=name) 
        cscr.tmpsrc     = op.abspath(filename)
        cscr.fileformat = fileformat
        cscr.dtype      = dtype
        # not load it by default!
        # cscr.data       = open(filename, 'r')
        cscr.src        = cscr.get_unique_relpath()
        return cscr
    
supermod.CScript.subclass = CScript
# end class CScript


class CImagestack(supermod.CImagestack, CBaseClass):
    def __init__(self, src=None, fileformat=None, name=None, pattern=None, description=None, metadata=None):
        super(CImagestack, self).__init__(src, fileformat, name, pattern, description, metadata, )
        
    def save(self):
        """ Save a loaded connectome object to a temporary file, return the path """
        raise NotImplementedError('Saving CImagestack not implemented yet.')
        
    def get_unique_relpath(self):
        """ Return a unique relative path for this element """
        return unify('CImagestack', self.name + '/')
    
supermod.CImagestack.subclass = CImagestack
# end class CImagestack



class subject(supermod.subject):
    def __init__(self, valueOf_=None):
        super(subject, self).__init__(valueOf_, )
supermod.subject.subclass = subject
# end class subject

class contributor(supermod.contributor):
    def __init__(self, valueOf_=None):
        super(contributor, self).__init__(valueOf_, )
supermod.contributor.subclass = contributor
# end class contributor


class date(supermod.date):
    def __init__(self, valueOf_=None):
        super(date, self).__init__(valueOf_, )
supermod.date.subclass = date
# end class date


class type_(supermod.type_):
    def __init__(self, valueOf_=None):
        super(type_, self).__init__(valueOf_, )
supermod.type_.subclass = type_
# end class type_


class format(supermod.format):
    def __init__(self, valueOf_=None):
        super(format, self).__init__(valueOf_, )
supermod.format.subclass = format
# end class format


class identifier(supermod.identifier):
    def __init__(self, valueOf_=None):
        super(identifier, self).__init__(valueOf_, )
supermod.identifier.subclass = identifier
# end class identifier


class source(supermod.source):
    def __init__(self, valueOf_=None):
        super(source, self).__init__(valueOf_, )
supermod.source.subclass = source
# end class source


class language(supermod.language):
    def __init__(self, valueOf_=None):
        super(language, self).__init__(valueOf_, )
supermod.language.subclass = language
# end class language


class coverage(supermod.coverage):
    def __init__(self, valueOf_=None):
        super(coverage, self).__init__(valueOf_, )
supermod.coverage.subclass = coverage
# end class coverage

class alternative(supermod.alternative):
    def __init__(self, valueOf_=None):
        super(alternative, self).__init__(valueOf_, )
supermod.alternative.subclass = alternative
# end class alternative


class tableOfContents(supermod.tableOfContents):
    def __init__(self, valueOf_=None):
        super(tableOfContents, self).__init__(valueOf_, )
supermod.tableOfContents.subclass = tableOfContents
# end class tableOfContents


class abstract(supermod.abstract):
    def __init__(self, valueOf_=None):
        super(abstract, self).__init__(valueOf_, )
supermod.abstract.subclass = abstract
# end class abstract

class valid(supermod.valid):
    def __init__(self, valueOf_=None):
        super(valid, self).__init__(valueOf_, )
supermod.valid.subclass = valid
# end class valid


class available(supermod.available):
    def __init__(self, valueOf_=None):
        super(available, self).__init__(valueOf_, )
supermod.available.subclass = available
# end class available


class issued(supermod.issued):
    def __init__(self, valueOf_=None):
        super(issued, self).__init__(valueOf_, )
supermod.issued.subclass = issued
# end class issued


class dateAccepted(supermod.dateAccepted):
    def __init__(self, valueOf_=None):
        super(dateAccepted, self).__init__(valueOf_, )
supermod.dateAccepted.subclass = dateAccepted
# end class dateAccepted


class dateCopyrighted(supermod.dateCopyrighted):
    def __init__(self, valueOf_=None):
        super(dateCopyrighted, self).__init__(valueOf_, )
supermod.dateCopyrighted.subclass = dateCopyrighted
# end class dateCopyrighted


class dateSubmitted(supermod.dateSubmitted):
    def __init__(self, valueOf_=None):
        super(dateSubmitted, self).__init__(valueOf_, )
supermod.dateSubmitted.subclass = dateSubmitted
# end class dateSubmitted


class extent(supermod.extent):
    def __init__(self, valueOf_=None):
        super(extent, self).__init__(valueOf_, )
supermod.extent.subclass = extent
# end class extent


class medium(supermod.medium):
    def __init__(self, valueOf_=None):
        super(medium, self).__init__(valueOf_, )
supermod.medium.subclass = medium
# end class medium


class isVersionOf(supermod.isVersionOf):
    def __init__(self, valueOf_=None):
        super(isVersionOf, self).__init__(valueOf_, )
supermod.isVersionOf.subclass = isVersionOf
# end class isVersionOf


class hasVersion(supermod.hasVersion):
    def __init__(self, valueOf_=None):
        super(hasVersion, self).__init__(valueOf_, )
supermod.hasVersion.subclass = hasVersion
# end class hasVersion


class isReplacedBy(supermod.isReplacedBy):
    def __init__(self, valueOf_=None):
        super(isReplacedBy, self).__init__(valueOf_, )
supermod.isReplacedBy.subclass = isReplacedBy
# end class isReplacedBy


class replaces(supermod.replaces):
    def __init__(self, valueOf_=None):
        super(replaces, self).__init__(valueOf_, )
supermod.replaces.subclass = replaces
# end class replaces


class isRequiredBy(supermod.isRequiredBy):
    def __init__(self, valueOf_=None):
        super(isRequiredBy, self).__init__(valueOf_, )
supermod.isRequiredBy.subclass = isRequiredBy
# end class isRequiredBy


class requires(supermod.requires):
    def __init__(self, valueOf_=None):
        super(requires, self).__init__(valueOf_, )
supermod.requires.subclass = requires
# end class requires


class isPartOf(supermod.isPartOf):
    def __init__(self, valueOf_=None):
        super(isPartOf, self).__init__(valueOf_, )
supermod.isPartOf.subclass = isPartOf
# end class isPartOf


class hasPart(supermod.hasPart):
    def __init__(self, valueOf_=None):
        super(hasPart, self).__init__(valueOf_, )
supermod.hasPart.subclass = hasPart
# end class hasPart


class isReferencedBy(supermod.isReferencedBy):
    def __init__(self, valueOf_=None):
        super(isReferencedBy, self).__init__(valueOf_, )
supermod.isReferencedBy.subclass = isReferencedBy
# end class isReferencedBy

class isFormatOf(supermod.isFormatOf):
    def __init__(self, valueOf_=None):
        super(isFormatOf, self).__init__(valueOf_, )
supermod.isFormatOf.subclass = isFormatOf
# end class isFormatOf


class hasFormat(supermod.hasFormat):
    def __init__(self, valueOf_=None):
        super(hasFormat, self).__init__(valueOf_, )
supermod.hasFormat.subclass = hasFormat
# end class hasFormat


class conformsTo(supermod.conformsTo):
    def __init__(self, valueOf_=None):
        super(conformsTo, self).__init__(valueOf_, )
supermod.conformsTo.subclass = conformsTo
# end class conformsTo


class spatial(supermod.spatial):
    def __init__(self, valueOf_=None):
        super(spatial, self).__init__(valueOf_, )
supermod.spatial.subclass = spatial
# end class spatial


class temporal(supermod.temporal):
    def __init__(self, valueOf_=None):
        super(temporal, self).__init__(valueOf_, )
supermod.temporal.subclass = temporal
# end class temporal


class audience(supermod.audience):
    def __init__(self, valueOf_=None):
        super(audience, self).__init__(valueOf_, )
supermod.audience.subclass = audience
# end class audience


class accrualMethod(supermod.accrualMethod):
    def __init__(self, valueOf_=None):
        super(accrualMethod, self).__init__(valueOf_, )
supermod.accrualMethod.subclass = accrualMethod
# end class accrualMethod


class accrualPeriodicity(supermod.accrualPeriodicity):
    def __init__(self, valueOf_=None):
        super(accrualPeriodicity, self).__init__(valueOf_, )
supermod.accrualPeriodicity.subclass = accrualPeriodicity
# end class accrualPeriodicity


class accrualPolicy(supermod.accrualPolicy):
    def __init__(self, valueOf_=None):
        super(accrualPolicy, self).__init__(valueOf_, )
supermod.accrualPolicy.subclass = accrualPolicy
# end class accrualPolicy


class instructionalMethod(supermod.instructionalMethod):
    def __init__(self, valueOf_=None):
        super(instructionalMethod, self).__init__(valueOf_, )
supermod.instructionalMethod.subclass = instructionalMethod
# end class instructionalMethod


class provenance(supermod.provenance):
    def __init__(self, valueOf_=None):
        super(provenance, self).__init__(valueOf_, )
supermod.provenance.subclass = provenance
# end class provenance


class rightsHolder(supermod.rightsHolder):
    def __init__(self, valueOf_=None):
        super(rightsHolder, self).__init__(valueOf_, )
supermod.rightsHolder.subclass = rightsHolder
# end class rightsHolder


class mediator(supermod.mediator):
    def __init__(self, valueOf_=None):
        super(mediator, self).__init__(valueOf_, )
supermod.mediator.subclass = mediator
# end class mediator


class educationLevel(supermod.educationLevel):
    def __init__(self, valueOf_=None):
        super(educationLevel, self).__init__(valueOf_, )
supermod.educationLevel.subclass = educationLevel
# end class educationLevel


class accessRights(supermod.accessRights):
    def __init__(self, valueOf_=None):
        super(accessRights, self).__init__(valueOf_, )
supermod.accessRights.subclass = accessRights
# end class accessRights


class bibliographicCitation(supermod.bibliographicCitation):
    def __init__(self, valueOf_=None):
        super(bibliographicCitation, self).__init__(valueOf_, )
supermod.bibliographicCitation.subclass = bibliographicCitation
# end class bibliographicCitation


class elementOrRefinementContainer(supermod.elementOrRefinementContainer):
    def __init__(self, any=None):
        super(elementOrRefinementContainer, self).__init__(any, )
supermod.elementOrRefinementContainer.subclass = elementOrRefinementContainer
# end class elementOrRefinementContainer


class SimpleLiteral(supermod.SimpleLiteral):
    def __init__(self, lang=None, valueOf_=None):
        super(SimpleLiteral, self).__init__(lang, valueOf_, )
supermod.SimpleLiteral.subclass = SimpleLiteral
# end class SimpleLiteral


class elementContainer(supermod.elementContainer):
    def __init__(self, any=None):
        super(elementContainer, self).__init__(any, )
supermod.elementContainer.subclass = elementContainer
# end class elementContainer


class TGN(supermod.TGN):
    def __init__(self, lang=None, valueOf_=None):
        super(TGN, self).__init__(lang, valueOf_, )
supermod.TGN.subclass = TGN
# end class TGN


class Box(supermod.Box):
    def __init__(self, lang=None, valueOf_=None):
        super(Box, self).__init__(lang, valueOf_, )
supermod.Box.subclass = Box
# end class Box


class ISO3166(supermod.ISO3166):
    def __init__(self, lang=None, valueOf_=None):
        super(ISO3166, self).__init__(lang, valueOf_, )
supermod.ISO3166.subclass = ISO3166
# end class ISO3166


class Point(supermod.Point):
    def __init__(self, lang=None, valueOf_=None):
        super(Point, self).__init__(lang, valueOf_, )
supermod.Point.subclass = Point
# end class Point


class RFC4646(supermod.RFC4646):
    def __init__(self, lang=None, valueOf_=None):
        super(RFC4646, self).__init__(lang, valueOf_, )
supermod.RFC4646.subclass = RFC4646
# end class RFC4646


class RFC3066(supermod.RFC3066):
    def __init__(self, lang=None, valueOf_=None):
        super(RFC3066, self).__init__(lang, valueOf_, )
supermod.RFC3066.subclass = RFC3066
# end class RFC3066


class RFC1766(supermod.RFC1766):
    def __init__(self, lang=None, valueOf_=None):
        super(RFC1766, self).__init__(lang, valueOf_, )
supermod.RFC1766.subclass = RFC1766
# end class RFC1766


class ISO639_3(supermod.ISO639_3):
    def __init__(self, lang=None, valueOf_=None):
        super(ISO639_3, self).__init__(lang, valueOf_, )
supermod.ISO639_3.subclass = ISO639_3
# end class ISO639_3


class ISO639_2(supermod.ISO639_2):
    def __init__(self, lang=None, valueOf_=None):
        super(ISO639_2, self).__init__(lang, valueOf_, )
supermod.ISO639_2.subclass = ISO639_2
# end class ISO639_2


class URI(supermod.URI):
    def __init__(self, lang=None, valueOf_=None):
        super(URI, self).__init__(lang, valueOf_, )
supermod.URI.subclass = URI
# end class URI


class IMT(supermod.IMT):
    def __init__(self, lang=None, valueOf_=None):
        super(IMT, self).__init__(lang, valueOf_, )
supermod.IMT.subclass = IMT
# end class IMT


class DCMIType(supermod.DCMIType):
    def __init__(self, lang=None, valueOf_=None):
        super(DCMIType, self).__init__(lang, valueOf_, )
supermod.DCMIType.subclass = DCMIType
# end class DCMIType


class W3CDTF(supermod.W3CDTF):
    def __init__(self, lang=None, valueOf_=None):
        super(W3CDTF, self).__init__(lang, valueOf_, )
supermod.W3CDTF.subclass = W3CDTF
# end class W3CDTF


class Period(supermod.Period):
    def __init__(self, lang=None, valueOf_=None):
        super(Period, self).__init__(lang, valueOf_, )
supermod.Period.subclass = Period
# end class Period


class UDC(supermod.UDC):
    def __init__(self, lang=None, valueOf_=None):
        super(UDC, self).__init__(lang, valueOf_, )
supermod.UDC.subclass = UDC
# end class UDC


class LCC(supermod.LCC):
    def __init__(self, lang=None, valueOf_=None):
        super(LCC, self).__init__(lang, valueOf_, )
supermod.LCC.subclass = LCC
# end class LCC


class DDC(supermod.DDC):
    def __init__(self, lang=None, valueOf_=None):
        super(DDC, self).__init__(lang, valueOf_, )
supermod.DDC.subclass = DDC
# end class DDC


class MESH(supermod.MESH):
    def __init__(self, lang=None, valueOf_=None):
        super(MESH, self).__init__(lang, valueOf_, )
supermod.MESH.subclass = MESH
# end class MESH


class LCSH(supermod.LCSH):
    def __init__(self, lang=None, valueOf_=None):
        super(LCSH, self).__init__(lang, valueOf_, )
supermod.LCSH.subclass = LCSH
# end class LCSH


class description(supermod.description):
    def __init__(self, valueOf_=None):
        super(description, self).__init__(valueOf_, )
    def export(self, outfile, level, namespace_='', name_='description', namespacedef_=''):
        super(description, self).export(outfile, level, namespace_='dcterms:', name_='description', namespacedef_='')
supermod.description.subclass = description
# end class description


class title(supermod.title):
    def __init__(self, valueOf_=None):
        super(title, self).__init__(valueOf_, )
    def export(self, outfile, level, namespace_='', name_='title', namespacedef_=''):
        super(title, self).export(outfile, level, namespace_='dcterms:', name_='title', namespacedef_='')
        
supermod.title.subclass = title
# end class title


class creator(supermod.creator):
    def __init__(self, valueOf_=None):
        super(creator, self).__init__(valueOf_, )
    def export(self, outfile, level, namespace_='', name_='creator', namespacedef_=''):
        super(creator, self).export(outfile, level, namespace_='dcterms:', name_='creator', namespacedef_='')
supermod.creator.subclass = creator
# end class creator

class publisher(supermod.publisher):
    def __init__(self, valueOf_=None):
        super(publisher, self).__init__(valueOf_, )
    def export(self, outfile, level, namespace_='', name_='publisher', namespacedef_=''):
        super(publisher, self).export(outfile, level, namespace_='dcterms:', name_='publisher', namespacedef_='')
supermod.publisher.subclass = publisher
# end class publisher

class relation(supermod.relation):
    def __init__(self, valueOf_=None):
        super(relation, self).__init__(valueOf_, )
    def export(self, outfile, level, namespace_='', name_='relation', namespacedef_=''):
        super(relation, self).export(outfile, level, namespace_='dcterms:', name_='relation', namespacedef_='')
supermod.relation.subclass = relation
# end class relation

class rights(supermod.rights):
    def __init__(self, valueOf_=None):
        super(rights, self).__init__(valueOf_, )
    def export(self, outfile, level, namespace_='', name_='rights', namespacedef_=''):
        super(rights, self).export(outfile, level, namespace_='dcterms:', name_='rights', namespacedef_='')
supermod.rights.subclass = rights
# end class rights

class created(supermod.created):
    def __init__(self, valueOf_=None):
        super(created, self).__init__(valueOf_, )
    def export(self, outfile, level, namespace_='', name_='created', namespacedef_=''):
        super(created, self).export(outfile, level, namespace_='dcterms:', name_='created', namespacedef_='')
supermod.created.subclass = created
# end class created

class modified(supermod.modified):
    def __init__(self, valueOf_=None):
        super(modified, self).__init__(valueOf_, )
    def export(self, outfile, level, namespace_='', name_='modified', namespacedef_=''):
        super(modified, self).export(outfile, level, namespace_='dcterms:', name_='modified', namespacedef_='')
supermod.modified.subclass = modified
# end class modified


class license(supermod.license):
    def __init__(self, valueOf_=None):
        super(license, self).__init__(valueOf_, )
    def export(self, outfile, level, namespace_='', name_='license', namespacedef_=''):
        super(license, self).export(outfile, level, namespace_='dcterms:', name_='license', namespacedef_='')
supermod.license.subclass = license
# end class license

class references(supermod.references):
    def __init__(self, valueOf_=None):
        super(references, self).__init__(valueOf_, )
    def export(self, outfile, level, namespace_='', name_='references', namespacedef_=''):
        super(references, self).export(outfile, level, namespace_='dcterms:', name_='references', namespacedef_='')
supermod.references.subclass = references
# end class references


def get_root_tag(node):
    tag = supermod.Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = None
    if hasattr(supermod, tag):
        rootClass = getattr(supermod, tag)
    return tag, rootClass


def parse(inFilename):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'property'
        rootClass = supermod.property
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('<?xml version="1.0" ?>\n')
    rootObj.export(sys.stdout, 0, name_=rootTag,
        namespacedef_='xmlns="http://www.connectomics.org/cff-2" xmlns:dcterms="http://purl.org/dc/terms/"')
    doc = None
    return rootObj


def parseString(inString):
    from StringIO import StringIO
    doc = parsexml_(StringIO(inString))
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'property'
        rootClass = supermod.property
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
#    sys.stdout.write('<?xml version="1.0" ?>\n')
#    rootObj.export(sys.stdout, 0, name_=rootTag,
#        namespacedef_='xmlns="http://www.connectomics.org/cff-2" xmlns:dcterms="http://purl.org/dc/terms/"')
    # update parent references
    
    return rootObj


def parseLiteral(inFilename):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'property'
        rootClass = supermod.property
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('#from cff import *\n\n')
    sys.stdout.write('import cff as model_\n\n')
    sys.stdout.write('rootObj = model_.property(\n')
    rootObj.exportLiteral(sys.stdout, 0, name_="property")
    sys.stdout.write(')\n')
    return rootObj


USAGE_TEXT = """
Usage: python ???.py <infilename>
"""

def usage():
    print USAGE_TEXT
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
    infilename = args[0]
    root = parse(infilename)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    main()

