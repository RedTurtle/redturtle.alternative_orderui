from zope.component import getMultiAdapter
from zope.interface import implements

from AccessControl import Unauthorized
from Acquisition import aq_parent, aq_inner
from OFS.interfaces import IOrderedContainer
from Products.ATContentTypes.interface import IATTopic
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

from plone.memoize import instance
from plone.app.content.browser.interfaces import IFolderContentsView
from tableview import Table, TableKSSView
from kss.core import KSSView

from plone.app.content.browser.foldercontents import FolderContentsView as BaseFolderContentsView

from Products.CMFPlone.interfaces import IPloneSiteRoot

import urllib

NOT_ADDABLE_TYPES = ('Favorite',)

class FolderContentsView(BaseFolderContentsView):
    """
    """
    
    def contents_table(self):
        table = FolderContentsTable(self.context, self.request)
        return table.render()      

class FolderContentsTable(object):
    """   
    The foldercontents table renders the table and its actions.
    """                

    def __init__(self, context, request, contentFilter={}):
        self.context = context
        self.request = request
        self.contentFilter = contentFilter

        url = self.context.absolute_url()
        view_url = url + '/@@folder_contents'
        self.table = Table(request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons)

    def render(self):
        return self.table.render()

    @property
    @instance.memoize
    def items(self):
        """
        """
        plone_utils = getToolByName(self.context, 'plone_utils')
        plone_view = getMultiAdapter((self.context, self.request), name=u'plone')
        portal_workflow = getToolByName(self.context, 'portal_workflow')
        portal_properties = getToolByName(self.context, 'portal_properties')
        site_properties = portal_properties.site_properties
        
        use_view_action = site_properties.getProperty('typesUseViewActionInListings', ())
        browser_default = self.context.browserDefault()
                
        if IATTopic.providedBy(self.context):
            contentsMethod = self.context.queryCatalog
        else:
            contentsMethod = self.context.getFolderContents
        
        results = []
        for i, obj in enumerate(contentsMethod(self.contentFilter)):
            if (i + 1) % 2 == 0:
                table_row_class = "draggable even"
            else:
                table_row_class = "draggable odd"

            url = obj.getURL()
            path = obj.getPath or "/".join(obj.getPhysicalPath())
            icon = plone_view.getIcon(obj);
            
            type_class = 'contenttype-' + plone_utils.normalizeString(
                obj.portal_type)

            review_state = obj.review_state
            state_class = 'state-' + plone_utils.normalizeString(review_state)
            relative_url = obj.getURL(relative=True)
            obj_type = obj.portal_type

            modified = plone_view.toLocalizedTime(
                obj.ModificationDate, long_format=1)
            
            if obj_type in use_view_action:
                view_url = url + '/view'
            elif obj.is_folderish:
                view_url = url + "/folder_contents"              
            else:
                view_url = url

            is_browser_default = len(browser_default[1]) == 1 and (
                obj.id == browser_default[1][0])
                                 
            results.append(dict(
                url = url,
                id  = obj.getId,
                quoted_id = urllib.quote_plus(obj.getId),
                path = path,
                title_or_id = obj.pretty_title_or_id(),
                description = obj.Description,
                obj_type = obj_type,
                size = obj.getObjSize,
                modified = modified,
                icon = icon.html_tag(),
                type_class = type_class,
                wf_state = review_state,
                state_title = portal_workflow.getTitleForStateOnType(review_state,
                                                           obj_type),
                state_class = state_class,
                is_browser_default = is_browser_default,
                folderish = obj.is_folderish,
                relative_url = relative_url,
                view_url = view_url,
                table_row_class = table_row_class,
                is_expired = self.context.isExpired(obj),
            ))
        return results

    @property
    def orderable(self):
        """
        """        
        return IOrderedContainer.providedBy(self.context)

    @property
    def show_sort_column(self):
        return self.orderable and self.editable
        
    @property
    def editable(self):
        """
        """
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        return context_state.is_editable()

    @property
    def buttons(self):
        buttons = []
        portal_actions = getToolByName(self.context, 'portal_actions')
        button_actions = portal_actions.listActionInfos(object=aq_inner(self.context), categories=('folder_buttons', ))

        # Do not show buttons if there is no data, unless there is data to be
        # pasted
        if not len(self.items):
            if self.context.cb_dataValid():
                for button in button_actions:
                    if button['id'] == 'paste':
                        return [self.setbuttonclass(button)]
            else:
                return []

        for button in button_actions:
            # Make proper classes for our buttons
            if button['id'] != 'paste' or self.context.cb_dataValid():
                buttons.append(self.setbuttonclass(button))
        return buttons

    def setbuttonclass(self, button):
        if button['id'] == 'paste':
            button['cssclass'] = 'standalone'
        else:
            button['cssclass'] = 'context'
        return button

class FolderContentsKSSView(TableKSSView):
    table = FolderContentsTable

