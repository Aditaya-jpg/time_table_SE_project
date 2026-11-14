<!DOCTYPE html>
<!-- 
 * Licensed to The Apereo Foundation under one or more contributor license
 * agreements. See the NOTICE file distributed with this work for
 * additional information regarding copyright ownership.
 *
 * The Apereo Foundation licenses this file to you under the Apache License,
 * Version 2.0 (the "License"); you may not use this file except in
 * compliance with the License. You may obtain a copy of the License at:
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * 
 -->
<%@ page language="java" pageEncoding="utf-8" contentType="text/html;charset=utf-8" errorPage="/error.jsp"%>
<%@ page import="org.unitime.localization.impl.Localization"%>
<%@ page import="org.unitime.timetable.util.Constants"%>
<%@ taglib uri="http://www.unitime.org/tags-custom" prefix="tt" %>
<%@ taglib uri="http://www.unitime.org/tags-localization" prefix="loc" %>
<loc:bundle name="CourseMessages">
<loc:bundle name="org.unitime.timetable.gwt.resources.GwtAriaMessages" id="ARIA">
<html lang='<%=Localization.getLanguage()%>' data-theme="dark">
  <head>
    <meta name="gwt:property" content="locale=<%=Localization.getFirstLocale()%>">
    <meta charset="UTF-8"/>
    <meta http-equiv="X-UA-Compatible" content="IE=Edge">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=2.0, user-scalable=yes">
    <script type="text/javascript">
    	(function() {
    		try {
    			var t = localStorage.getItem('unitime-theme') || 'dark';
    			document.documentElement.setAttribute('data-theme', t);
    		} catch(e) {}
    	})();
    </script>
    <link type="text/css" rel="stylesheet" href="unitime/gwt/standard/standard.css">
    <link type="text/css" rel="stylesheet" href="styles/unitime.css">
    <link type="text/css" rel="stylesheet" href="styles/unitime-mobile.css">
    <!--[if IE]>
	    <link type="text/css" rel="stylesheet" href="styles/unitime-ie.css">
    <![endif]-->
    <loc:rtl><link type="text/css" rel="stylesheet" href="styles/unitime-rtl.css"></loc:rtl>
	<link rel="stylesheet" type="text/css" href="styles/timetabling.css">
	<link rel="stylesheet" type="text/css" href="styles/modern-rework.css?v=apple_v6">
    <tt:hasProperty name="tmtbl.addon.css">
    	<link rel="stylesheet" type="text/css" href="%tmtbl.addon.css%" />
    </tt:hasProperty>
    <tt:hasProperty name="tmtbl.custom.css">
    	<link rel="stylesheet" type="text/css" href="%tmtbl.custom.css%" />
    </tt:hasProperty>
    <link rel="shortcut icon" href="images/timetabling.ico">
    <title>PEC Timetable Scheduler | Punjab Engineering College</title>
    <script type="text/javascript" src="scripts/rtt.js"></script>
  </head>
  <body class="unitime-Body">
    <iframe src="javascript:''" id="__gwt_historyFrame" tabIndex="-1" style="position:absolute;width:0;height:0;border:0"></iframe>
    <iframe src="javascript:''" id="__printingFrame" tabIndex="-1" style="position:absolute;width:0;height:0;border:0"></iframe>
    
    <span class='top-menu'>
    	<tt:notHasProperty name="unitime.menu.style" user="true">
	    	<span id='UniTimeGWT:DynamicTopMenu' style="display: block; height: 23px;"></span>
    	</tt:notHasProperty>
    	<tt:propertyEquals name="unitime.menu.style" user="true" value="Dynamic On Top">
    		<span id='UniTimeGWT:DynamicTopMenu' style="display: block; height: 23px;"></span>
    	</tt:propertyEquals>
    	<tt:propertyEquals name="unitime.menu.style" user="true" value="Static On Top">
    		<span id='UniTimeGWT:TopMenu' style="display: block; height: 23px;"></span>
    	</tt:propertyEquals>
    </span>
    
	<tt:hasProperty name="tmtbl.global.info">
    	<div class='unitime-PageMessage'><tt:property name="tmtbl.global.info"/></div>
	</tt:hasProperty>
	<tt:hasProperty name="tmtbl.global.warn">
    	<div class='unitime-PageWarn'><tt:property name="tmtbl.global.warn"/></div>
	</tt:hasProperty>
	<tt:hasProperty name="tmtbl.global.error">
    	<div class='unitime-PageError'><tt:property name="tmtbl.global.error"/></div>
	</tt:hasProperty>
	<tt:page-warning prefix="tmtbl.page.warn." style="unitime-PageWarn"/>
	<tt:page-warning prefix="tmtbl.page.info." style="unitime-PageMessage"/>
	<tt:page-warning prefix="tmtbl.page.error." style="unitime-PageError"/>
	<span id='UniTimeGWT:CustomPageMessages'></span>
	<span id='UniTimeGWT:SolverWarnings'></span>
	<tt:offering-locks/>
  	
	<span class="unitime-Page"><span class='row'>
	<span class='sidebar' id="unitime-SideMenu">
    		<tt:propertyEquals name="unitime.menu.style" user="true" value="Stack On Side">
    			<span id='UniTimeGWT:SideStackMenu' style="display: block;" ></span>
	    	</tt:propertyEquals>
    		<tt:propertyEquals name="unitime.menu.style" user="true" value="Tree On Side">
    			<span id='UniTimeGWT:SideTreeMenu' style="display: block;" ></span>
	    	</tt:propertyEquals>
    		<tt:propertyEquals name="unitime.menu.style" user="true" value="Static Stack On Side">
    			<span id='UniTimeGWT:StaticSideStackMenu' style="display: block;" ></span>
		    </tt:propertyEquals>
    		<tt:propertyEquals name="unitime.menu.style" user="true" value="Static Tree On Side">
    			<span id='UniTimeGWT:StaticSideTreeMenu' style="display: block;" ></span>
		    </tt:propertyEquals>
    		<tt:propertyEquals name="unitime.menu.style" user="true" value="Dynamic Stack On Side">
    			<span id='UniTimeGWT:SideStackMenu' style="display: block;" ></span>
		    </tt:propertyEquals>
    		<tt:propertyEquals name="unitime.menu.style" user="true" value="Dynamic Tree On Side">
    			<span id='UniTimeGWT:SideTreeMenu' style="display: block;" ></span>
		    </tt:propertyEquals>
    <script type="text/javascript">
    	var sideMenu = document.getElementById("unitime-SideMenu").getElementsByTagName("span");
    	if (sideMenu.length > 0) {
    		var c = unescape(document.cookie);
    		var c_start = c.indexOf("UniTime:SideBar=");
    		if (c_start >= 0) {
    			c_start = c.indexOf("|W:", c_start) + 3;
    			var c_end = c.indexOf(";", c_start);
    			if (c_end < 0) c_end=c.length;
    			var width = c.substring(c_start, c_end);
    			sideMenu[0].style.width = width + "px";
    			// alert(c.substring(c.indexOf("UniTime:SideBar=") + 16, c_end));
    		} else {
    			sideMenu[0].style.width = (sideMenu[0].id.indexOf("StackMenu") >= 0 ? "172px" : "152px");
    		}
    	}
    </script>
	</span>
    <span class='main'><span class='body' id="unitime-Page">
    	<span class="unitime-PageHeader" id="unitime-Header">
    		<span class="row">
    			<span class="mobile-menu-button" id='UniTimeGWT:MobileMenuButton'></span>
    			<a href='main.action' tabIndex="-1" class="logo" aria-label="${ARIA.pageUniTimeLogo()}"></a>
    			<span class="content">
					<span id='UniTimeGWT:Title' class="title"></span>
					<span class='unitime-Header'><span id='UniTimeGWT:Header' class="unitime-InfoPanel"></span></span>
					<span id='UniTimeGWT:TitlePanel' class='navigation'></span>
				</span>
			</span>
		</span>
		<span class="mobile-menu" id='UniTimeGWT:MobileMenuPanel'></span>
		<span class="content"> 
			<span id="UniTimeGWT:Loading" class="unitime-PageLoading"><loc:message name="messagePageLoading"/></span>
	    	<span id='UniTimeGWT:Body'></span>
	    </span>
    </span><span class='footer' id="unitime-Footer">
		<span class="unitime-Footer">
			<span class="row">
				<span class="cell left">
					<span id='UniTimeGWT:Version'></span>
				</span>
    			<%-- WARNING: Changing or removing the copyright notice will violate the license terms. If you need a different licensing, please contact us at support@unitime.org --%>
				<span class="cell middle"><tt:copy/></span>
				<span class="cell right" id='UniTimeGWT:Registration'><tt:registration/></span>
			</span>
		</span>
		<tt:hasProperty name="tmtbl.page.disclaimer">
			<span class='unitime-Disclaimer'><tt:property name="tmtbl.page.disclaimer"/></span>
		</tt:hasProperty>
		<span class="unitime-VisibleAriaStatus" id='UniTimeGWT:AriaStatus'></span>
	</span>
</span></span></span>

    <script type="text/javascript" src="unitime/unitime.nocache.js"></script>

	<!-- Theme Switcher Floating Button -->
	<button id="themeToggleBtn" class="theme-toggle-btn" aria-label="Toggle Theme" title="Toggle Dark/Light Glassmorphism Theme">
		<svg id="themeIconSun" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
			<circle cx="12" cy="12" r="5"></circle>
			<line x1="12" y1="1" x2="12" y2="3"></line>
			<line x1="12" y1="21" x2="12" y2="23"></line>
			<line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
			<line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
			<line x1="1" y1="12" x2="3" y2="12"></line>
			<line x1="21" y1="12" x2="23" y2="12"></line>
			<line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
			<line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
		</svg>
		<svg id="themeIconMoon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display: none;">
			<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
		</svg>
	</button>
	<script type="text/javascript">
		(function() {
			var currentTheme = localStorage.getItem('unitime-theme') || 'dark';
			document.documentElement.setAttribute('data-theme', currentTheme);
			function updateIcon(theme) {
				var sun = document.getElementById('themeIconSun');
				var moon = document.getElementById('themeIconMoon');
				if (sun && moon) {
					if (theme === 'light') {
						sun.style.display = 'none';
						moon.style.display = 'block';
					} else {
						sun.style.display = 'block';
						moon.style.display = 'none';
					}
				}
			}
			updateIcon(currentTheme);
			var btn = document.getElementById('themeToggleBtn');
			if (btn) {
				btn.addEventListener('click', function() {
					var next = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
					document.documentElement.setAttribute('data-theme', next);
					localStorage.setItem('unitime-theme', next);
					updateIcon(next);
				});
			}
		})();
	</script>
  </body>
</html>
</loc:bundle></loc:bundle>