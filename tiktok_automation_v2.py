# tiktok_automation_v2.py - ROLEX-GRADE PRECISION

import asyncio
import random
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from typing import Optional, Dict, Tuple
from logger_system import *
from anti_detection import AntiDetectionSystem
from dolphin_integration import dolphin

class TikTokAutomationV2:
    """
    Production-grade TikTok automation
    Every action logged, every decision tracked
    """
    
    def __init__(self, cookie_manager):
        self.cookie_manager = cookie_manager
        self.anti_detection = AntiDetectionSystem()
        
        # Timing parameters (optimized by Dolphin-X1)
        self.timing = {
            'video_watch_min': 15,
            'video_watch_max': 30,
            'scroll_delay_min': 1,
            'scroll_delay_max': 3,
            'typing_speed_base': 0.15,
            'action_delay_min': 2,
            'action_delay_max': 5,
            'comment_review_time': (2, 4),
            'post_comment_wait': (3, 5)
        }
        
        # Selector strategies (multiple fallbacks)
        self.selectors = {
            'comment_box': [
                'div[data-e2e="comment-input"]',
                'div[contenteditable="true"][data-e2e="comment-input"]',
                'div.public-DraftEditor-content',
                '[placeholder*="comment" i]',
                'div[role="textbox"]'
            ],
            'post_button': [
                'button[data-e2e="comment-post"]',
                'button:has-text("Post")',
                'div[data-e2e="comment-post"]',
                'button[type="submit"]'
            ],
            'video_player': [
                'video',
                'div[data-e2e="video-player"]',
                '.video-player'
            ]
        }
        
        affilify_logger.main_logger.info("🤖 TikTok Automation V2 initialized")
    
    async def post_comment(
        self,
        username: str,
        video_url: str,
        comment_text: str
    ) -> Tuple[bool, str, Dict]:
        """
        Post comment with FULL logging and error recovery
        
        Returns: (success, message, metadata)
        """
        
        start = log_start("PostComment", username=username, video_url=video_url, comment_preview=comment_text[:50])
        
        metadata = {
            'username': username,
            'video_url': video_url,
            'comment_length': len(comment_text),
            'timestamps': {},
            'errors': [],
            'selectors_tried': [],
            'actions_performed': []
        }
        
        context = None
        page = None
        
        try:
            # ===== STEP 1: CREATE BROWSER CONTEXT =====
            step_start = datetime.now()
            log_account(username, "CreateBrowserContext", "STARTED")
            
            context = await self.cookie_manager.create_browser_context(username, headless=False)
            if not context:
                log_account(username, "CreateBrowserContext", "FAILED", reason="Context creation failed")
                log_end("PostComment", start, False, error="Context creation failed")
                return False, "Failed to create browser context", metadata
            
            await self.anti_detection.prepare_browser_context(context)
            metadata['timestamps']['context_created'] = (datetime.now() - step_start).total_seconds()
            metadata['actions_performed'].append('context_created')
            
            log_account(username, "CreateBrowserContext", "SUCCESS", duration=metadata['timestamps']['context_created'])
            
            # ===== STEP 2: OPEN PAGE =====
            step_start = datetime.now()
            log_account(username, "OpenPage", "STARTED", url=video_url)
            
            page = await context.new_page()
            metadata['actions_performed'].append('page_opened')
            
            # ===== STEP 3: NAVIGATE TO VIDEO =====
            step_start = datetime.now()
            log_account(username, "NavigateToVideo", "STARTED", url=video_url)
            
            await self.anti_detection.navigate_like_human(page, video_url)
            metadata['timestamps']['navigation'] = (datetime.now() - step_start).total_seconds()
            metadata['actions_performed'].append('navigated')
            
            log_account(username, "NavigateToVideo", "SUCCESS", duration=metadata['timestamps']['navigation'])
            
            # ===== STEP 4: WATCH VIDEO (CRITICAL) =====
            step_start = datetime.now()
            watch_duration = random.uniform(self.timing['video_watch_min'], self.timing['video_watch_max'])
            log_account(username, "WatchVideo", "STARTED", planned_duration=f"{watch_duration:.1f}s")
            
            await self._watch_video_with_logging(page, watch_duration, metadata)
            metadata['timestamps']['video_watched'] = (datetime.now() - step_start).total_seconds()
            metadata['actions_performed'].append('video_watched')
            
            log_account(username, "WatchVideo", "SUCCESS", actual_duration=metadata['timestamps']['video_watched'])
            
            # ===== STEP 5: SCROLL TO COMMENTS =====
            step_start = datetime.now()
            log_account(username, "ScrollToComments", "STARTED")
            
            await self.anti_detection.human_behavior.natural_scroll(page, distance=400)
            await asyncio.sleep(random.uniform(*self.timing['comment_review_time']))
            metadata['timestamps']['scrolled'] = (datetime.now() - step_start).total_seconds()
            metadata['actions_performed'].append('scrolled_to_comments')
            
            log_account(username, "ScrollToComments", "SUCCESS")
            
            # ===== STEP 6: FIND COMMENT BOX (WITH FALLBACKS) =====
            step_start = datetime.now()
            log_account(username, "FindCommentBox", "STARTED")
            
            comment_box_selector = await self._find_element_with_fallbacks(
                page, 
                self.selectors['comment_box'],
                'comment box',
                metadata
            )
            
            if not comment_box_selector:
                # AI TO THE RESCUE
                log_account(username, "FindCommentBox", "FAILED_ATTEMPTING_AI_RECOVERY")
                
                html = await page.content()
                new_selectors = await dolphin.generate_selector_alternatives(
                    "comment box",
                    html
                )
                
                if new_selectors:
                    metadata['selectors_tried'].extend(new_selectors)
                    for selector in new_selectors:
                        try:
                            element = await page.query_selector(selector)
                            if element:
                                comment_box_selector = selector
                                log_account(username, "FindCommentBox", "SUCCESS_VIA_AI", selector=selector)
                                break
                        except:
                            continue
                
                if not comment_box_selector:
                    log_account(username, "FindCommentBox", "FAILED_PERMANENTLY")
                    log_end("PostComment", start, False, error="Comment box not found")
                    return False, "Could not find comment box", metadata
            
            metadata['timestamps']['comment_box_found'] = (datetime.now() - step_start).total_seconds()
            metadata['actions_performed'].append('comment_box_found')
            
            # ===== STEP 7: CLICK COMMENT BOX =====
            step_start = datetime.now()
            log_account(username, "ClickCommentBox", "STARTED", selector=comment_box_selector)
            
            hover_success = await self.anti_detection.human_behavior.hover_before_click(page, comment_box_selector)
            if not hover_success:
                log_account(username, "ClickCommentBox", "HOVER_FAILED")
            
            await page.click(comment_box_selector)
            await asyncio.sleep(random.uniform(0.5, 1.5))
            metadata['actions_performed'].append('comment_box_clicked')
            
            log_account(username, "ClickCommentBox", "SUCCESS")
            
            # ===== STEP 8: TYPE COMMENT (HUMAN SIMULATION) =====
            step_start = datetime.now()
            log_account(username, "TypeComment", "STARTED", comment=comment_text[:50])
            
            await self.anti_detection.human_typing.type_like_human(page, comment_box_selector, comment_text)
            metadata['timestamps']['typing_completed'] = (datetime.now() - step_start).total_seconds()
            metadata['actions_performed'].append('comment_typed')
            
            log_account(username, "TypeComment", "SUCCESS", duration=metadata['timestamps']['typing_completed'])
            
            # ===== STEP 9: REVIEW COMMENT =====
            review_time = random.uniform(*self.timing['comment_review_time'])
            log_account(username, "ReviewComment", "STARTED", duration=f"{review_time:.1f}s")
            await asyncio.sleep(review_time)
            metadata['actions_performed'].append('comment_reviewed')
            log_account(username, "ReviewComment", "SUCCESS")
            
            # ===== STEP 10: FIND POST BUTTON =====
            step_start = datetime.now()
            log_account(username, "FindPostButton", "STARTED")
            
            post_button_selector = await self._find_element_with_fallbacks(
                page,
                self.selectors['post_button'],
                'post button',
                metadata
            )
            
            if not post_button_selector:
                log_account(username, "FindPostButton", "FAILED")
                log_end("PostComment", start, False, error="Post button not found")
                return False, "Could not find post button", metadata
            
            log_account(username, "FindPostButton", "SUCCESS", selector=post_button_selector)
            
            # ===== STEP 11: CLICK POST BUTTON =====
            log_account(username, "ClickPostButton", "STARTED")
            
            hover_success = await self.anti_detection.human_behavior.hover_before_click(page, post_button_selector)
            await page.click(post_button_selector)
            metadata['actions_performed'].append('post_button_clicked')
            
            log_account(username, "ClickPostButton", "SUCCESS")
            
            # ===== STEP 12: WAIT AND VERIFY =====
            wait_time = random.uniform(*self.timing['post_comment_wait'])
            log_account(username, "VerifyCommentPosted", "STARTED", wait_time=f"{wait_time:.1f}s")
            await asyncio.sleep(wait_time)
            
            # Check for error messages
            error_detected = await self._check_for_errors(page, metadata)
            
            if error_detected:
                log_account(username, "VerifyCommentPosted", "ERROR_DETECTED", error=error_detected)
                log_end("PostComment", start, False, error=error_detected)
                return False, f"TikTok error: {error_detected}", metadata
            
            # Take success screenshot
            screenshot_path = f"screenshots/success_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
            metadata['screenshot'] = screenshot_path
            
            log_account(username, "VerifyCommentPosted", "SUCCESS")
            
            # ===== SUCCESS! =====
            total_duration = (datetime.now() - start).total_seconds()
            metadata['timestamps']['total_duration'] = total_duration
            
            log_comment(username, video_url, comment_text, True, metadata=metadata)
            log_end("PostComment", start, True, **metadata['timestamps'])
            
            return True, "Comment posted successfully", metadata
            
        except PlaywrightTimeout as e:
            error_msg = f"Timeout: {str(e)}"
            metadata['errors'].append(error_msg)
            log_error("PlaywrightTimeout", error_msg, context={'username': username, 'video_url': video_url})
            log_account(username, "PostComment", "TIMEOUT", error=error_msg)
            log_end("PostComment", start, False, error="timeout")
            return False, error_msg, metadata
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            metadata['errors'].append(error_msg)
            log_error("PostCommentException", error_msg, stack_trace=str(e), context={'username': username})
            log_account(username, "PostComment", "EXCEPTION", error=error_msg)
            log_end("PostComment", start, False, error=str(e))
            return False, error_msg, metadata
            
        finally:
            # CLEANUP
            if context:
                await self.cookie_manager.close_context(username)
                log_account(username, "Cleanup", "SUCCESS")
    
    async def _watch_video_with_logging(self, page, duration: float, metadata: Dict):
        """
        Watch video with detailed action logging
        """
        elapsed = 0
        actions_taken = []
        
        while elapsed < duration:
            chunk = random.uniform(3, 7)
            await asyncio.sleep(chunk)
            elapsed += chunk
            
            # Random interactions
            action_roll = random.random()
            
            if action_roll < 0.1:  # 10% - scroll to comments
                await self.anti_detection.human_behavior.natural_scroll(page, distance=200)
                actions_taken.append('scroll_to_comments')
                await asyncio.sleep(random.uniform(1, 2))
                await self.anti_detection.human_behavior.natural_scroll(page, distance=-200)
                actions_taken.append('scroll_back')
            
            elif action_roll < 0.15:  # 5% - pause video
                video = await page.query_selector('video')
                if video:
                    box = await video.bounding_box()
                    if box:
                        await page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                        actions_taken.append('pause_video')
                        await asyncio.sleep(random.uniform(2, 4))
                        await page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                        actions_taken.append('resume_video')
        
        metadata['video_watch_actions'] = actions_taken
    
    async def _find_element_with_fallbacks(self, page, selectors: list, element_name: str, metadata: Dict) -> Optional[str]:
        """
        Try multiple selectors with logging
        """
        for selector in selectors:
            metadata['selectors_tried'].append({'element': element_name, 'selector': selector})
            
            try:
                element = await page.query_selector(selector)
                if element:
                    affilify_logger.main_logger.debug(f"✅ Found {element_name} with: {selector}")
                    return selector
            except Exception as e:
                affilify_logger.main_logger.debug(f"❌ Selector failed: {selector} | {e}")
                continue
        
        affilify_logger.main_logger.warning(f"⚠️ All selectors failed for: {element_name}")
        return None
    
    async def _check_for_errors(self, page, metadata: Dict) -> Optional[str]:
        """
        Check for TikTok error messages and handle captchas
        """
        # First, check for captchas
        try:
            content = await page.content()
            if "verify" in content.lower() or "captcha" in content.lower():
                affilify_logger.main_logger.info("🛡️ Captcha detected during automation. SadCaptcha extension will handle it...")
                # SadCaptcha is integrated at browser level, just wait for it to solve
                await asyncio.sleep(10)
        except Exception as e:
            affilify_logger.main_logger.error(f"❌ Error during captcha check/solve: {e}")

        error_selectors = [
            'text="Please try again later"',
            'text="Too many attempts"',
            'text="Unable to post"',
            'text="This comment may be inappropriate"',
            'div[data-e2e="error-message"]'
        ]
        
        for selector in error_selectors:
            try:
                error_element = await page.query_selector(selector)
                if error_element:
                    error_text = await error_element.inner_text()
                    return error_text
            except:
                continue
        
        return None
    
    async def update_timing_from_ai(self):
        """
        Let Dolphin-X1 optimize timing based on performance
        """
        # This would be called periodically
        # Fetch recent success/failure logs
        # Send to Dolphin-X1 for analysis
        # Update self.timing with recommendations
        pass
