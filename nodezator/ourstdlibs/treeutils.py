"""Common utilities for handling tree-structured data."""

from collections.abc import Mapping


### function to merge dicts representing trees
### (dicts are nested or not)


def merge_nested_dicts(*dicts):
    """Return new dict from given ones.

    It works similarly to dict(ChainMap(*dicts)),
    but the difference is that nested dicts can
    be passed as well.

    It was written to merge translation maps, the
    first being the default one (fallback) and the
    second one having priority. However, we wrote
    the function in a way that any number of dicts
    can be merged, with first dicts having priority
    over the last ones for defining leaves.

    Parameters
    ==========
    *dicts (mappings)
        mappings to be merged; mappings passed first
        have priority when defining leaves.
    """
    ### create list to store all branch lists
    branch_lists = []

    ### for each given dict, extract a branch list
    ### and append it

    for d in dicts:

        branch_list = []
        branch_list.extend(_yield_branch_objects([], d))
        branch_lists.append(branch_list)

    ### create a dict to store the items resulting
    ### from merging the dicts
    tree = {}

    ### for each branch list, implant the nodes of
    ### each branch in the tree

    for branch_list in branch_lists:
        for branch in branch_list:
            _implant_nodes(tree, branch)

    ### finally return the resulting tree/dict
    return tree


def _yield_branch_objects(branch, node):
    """Yield each subbranch for each given branch.

    A subbranch is represented by a dict with the 'leaf'
    key containing the leaf node and the 'stem' key
    containing a list of all nodes leading to the leaf.

    Parameters
    ==========
    branch (list)
        node objects leading to the leaf.
    node (dict)
        a node containing more nodes and/or leaves.
    """
    ### iterate over all items in the given node

    for key, value in node.items():

        ## if the value is a mapping, then we look deeper
        ## into the branch

        if isinstance(value, Mapping):

            yield from _yield_branch_objects(branch[:] + [key], value)

        ## otherwise the value is a leaf; we can finally
        ## yield it along with its stem, both inside a
        ## dict representing the branch

        else:
            yield {
                "stem": branch[:] + [key],
                "leaf": value,
            }


def _implant_nodes(tree, branch):
    """Implant nodes of branch in the given tree.

    common nodes and leaf nodes are only implanted if they
    do not already exist in the tree.

    Parameters
    ==========
    tree (dict)
        the dictionary wherein to implant the nodes.

    branch (dict)
        represents a branch; its 'leaf' key has
        a leaf node and its 'stem' key has a
        list of all nodes from the first to
        the last one leading to the leaf.
    """
    ### retreive stem and leaf of branch

    stem = branch["stem"]
    leaf = branch["leaf"]

    ### since we'll use list.pop() to obtain
    ### each node of the stem, we reverse its
    ### order so the first ones are popped out
    ### first from the end of the list
    stem.reverse()

    ### while not reaching the break point...

    while True:

        ### pop a node from the stem
        node = stem.pop()

        ### if there are no nodes left in the stem...

        if not stem:

            ## if the node isn't in the tree, plant
            ## the leaf there

            if node not in tree:
                tree[node] = leaf

            ## break out of the "while loop"
            break

        else:

            ## if the node isn't in the tree, plant
            ## an empty dict there, and make the
            ## dict the new tree, by assigning it
            ## to the tree variable;
            ##
            ## note that these assignment operations
            ## would NOT work if chained like so:
            ## tree = tree[node] = {}

            if node not in tree:

                tree[node] = {}
                tree = tree[node]

            else:
                tree = tree[node]


### function to yield attributes from tree leaves


def yield_tree_attrs(tree, attr_name, children_attr_name):
    """Yield specific attributes in objects in a tree.

    Parameters
    ==========
    tree (any python object)
        object which might contain children objects.
    attr_name (string)
        name of attribute whose value you want to yield
        for each object of the tree.
    children_attr_name (string)
        name of attribute wherein to find more children.
    """
    ### yield attributes from each children, if there are
    ### children

    try:
        children = getattr(tree, children_attr_name)

    except AttributeError:
        pass

    else:

        for child in children:

            yield from yield_tree_attrs(child, attr_name, children_attr_name)

    ### yield attribute from the object itself, if it has
    ### such attribute

    try:
        value = getattr(tree, attr_name)
    except AttributeError:
        pass
    else:
        yield value
