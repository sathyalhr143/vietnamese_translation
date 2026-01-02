"""Audio capture and transcription module."""

import sounddevice as sd
import numpy as np
from typing import Dict, List
from src.models import AudioData, TranscriptionResult, AudioProcessingConfig
from src.logger import get_logger
import os
from pydub import AudioSegment
import io

logger = get_logger(__name__)

# Maximum file size for Whisper API (25 MB)
MAX_WHISPER_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
# Target chunk size (20 MB to be safe)
TARGET_CHUNK_SIZE = 20 * 1024 * 1024  # 20 MB


class AudioProcessor:
    """Handle audio capture and processing with Whisper transcription."""
    
    def __init__(self, config: AudioProcessingConfig = None):
        """
        Initialize audio processor.
        
        Args:
            config: AudioProcessingConfig instance. If None, uses defaults.
        """
        self.config = config or AudioProcessingConfig()
        self.whisper_model = None
        self.load_whisper_model(self.config.model_size)
    
    def load_whisper_model(self, model_size: str = "small"):
        """
        Load OpenAI Whisper model.
        
        Args:
            model_size: Model size (tiny, base, small, medium, large)
        """
        try:
            import whisper
            logger.info(f"Loading Whisper model: {model_size}")
            self.whisper_model = whisper.load_model(model_size, )
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            raise
    
    def record_audio(self, duration: int = None) -> AudioData:
        """
        Record audio from microphone.
        
        Args:
            duration: Recording duration in seconds. If None, uses config value.
            
        Returns:
            AudioData instance
        """
        if duration is None:
            duration = self.config.chunk_duration
        
        try:
            logger.info(f"Recording audio for {duration} seconds...")
            audio_data = sd.rec(
                int(duration * self.config.sample_rate),
                samplerate=self.config.sample_rate,
                channels=1,
                dtype=np.float32
            )
            sd.wait()
            logger.info("Audio recording completed")
            
            return AudioData(
                data=audio_data.flatten().tolist(),
                sample_rate=self.config.sample_rate,
                duration_seconds=duration
            )
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            raise
    
    def transcribe_audio(self, audio: AudioData) -> TranscriptionResult:
        """
        Transcribe audio using Whisper.
        
        Args:
            audio: AudioData instance
            
        Returns:
            TranscriptionResult instance
        """
        if self.whisper_model is None:
            self.load_whisper_model(self.config.model_size)
        
        try:
            logger.info("Transcribing audio with Whisper...")
            
            # Convert list back to numpy array
            audio_array = np.array(audio.data, dtype=np.float32)
            
            # checking the language set in config
            print(self.config.language, "language given to whisper")
            
            result = self.whisper_model.transcribe(
                audio_array,
                language=self.config.language,
                fp16=False  # Use FP32 for CPU compatibility
            )
            
            text = result['text'].strip()
            logger.info(f"Transcription completed: {text}")
            
            # Calculate average confidence from segments
            confidence = 0.0
            if 'segments' in result and result['segments']:
                confidences = [seg.get('avg_logprob', 0.0) for seg in result['segments']]
                # Convert log probabilities to confidence scores (0-1 range)
                # avg_logprob is typically between -1 and 0, with 0 being highest confidence
                confidence = np.mean([np.exp(c) for c in confidences]) if confidences else 0.0
            
            return TranscriptionResult(
                text=text,
                language=self.config.language,
                confidence=confidence,
                duration=audio.duration_seconds
            )
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise    
    def transcribe_audio_from_file(self, file_path: str) -> TranscriptionResult:
        """
        Transcribe audio from a file (supports WAV, MP3, OGG, FLAC, etc.).
        
        Args:
            file_path: Path to audio file
            
        Returns:
            TranscriptionResult instance
        """
        if self.whisper_model is None:
            self.load_whisper_model(self.config.model_size)
        
        try:
            logger.info(f"Transcribing audio file: {file_path}")
            
            result = self.whisper_model.transcribe(
                file_path,
                language=self.config.language,
                fp16=False  # Use FP32 for CPU compatibility
            )
            
            text = result['text'].strip()
            logger.info(f"Transcription completed: {text}")
            
            # Calculate average confidence from segments
            confidence = 0.0
            if 'segments' in result and result['segments']:
                confidences = [seg.get('avg_logprob', 0.0) for seg in result['segments']]
                # Convert log probabilities to confidence scores (0-1 range)
                # avg_logprob is typically between -1 and 0, with 0 being highest confidence
                confidence = np.mean([np.exp(c) for c in confidences]) if confidences else 0.0
            
            # Get duration from Whisper result
            duration = result.get('duration', 0.0)
            
            return TranscriptionResult(
                text=text,
                language=self.config.language,
                confidence=confidence,
                duration=duration
            )
        except Exception as e:
            logger.error(f"Error transcribing audio file: {e}")
            raise
    
    def split_audio_file(self, file_path: str, max_chunk_size: int = TARGET_CHUNK_SIZE) -> List[str]:
        """
        Split large audio file into smaller chunks for Whisper processing.
        
        Args:
            file_path: Path to audio file
            max_chunk_size: Maximum size per chunk in bytes
            
        Returns:
            List of temporary file paths for chunks
        """
        try:
            file_size = os.path.getsize(file_path)
            
            # If file is small enough, return as-is
            if file_size <= max_chunk_size:
                return [file_path]
            
            logger.info(f"Splitting large audio file ({file_size / 1024 / 1024:.1f} MB) into chunks...")
            
            # Load audio and calculate chunks by duration
            audio = AudioSegment.from_file(file_path)
            duration_ms = len(audio)  # Duration in milliseconds
            
            # Calculate chunk duration based on file size ratio
            chunk_duration_ms = int((max_chunk_size / file_size) * duration_ms)
            
            chunks = []
            temp_dir = "/tmp/audio_chunks"
            os.makedirs(temp_dir, exist_ok=True)
            
            chunk_count = 0
            current_pos = 0
            
            while current_pos < duration_ms:
                chunk_end = min(current_pos + chunk_duration_ms, duration_ms)
                chunk_audio = audio[current_pos:chunk_end]
                
                chunk_file = os.path.join(temp_dir, f"chunk_{chunk_count:03d}.mp3")
                chunk_audio.export(chunk_file, format="mp3", bitrate="128k")
                chunks.append(chunk_file)
                
                logger.info(f"Created chunk {chunk_count}: {os.path.getsize(chunk_file) / 1024 / 1024:.1f} MB")
                
                current_pos = chunk_end
                chunk_count += 1
            
            logger.info(f"Created {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting audio file: {e}")
            raise
    
    def transcribe_audio_from_file_chunked(self, file_path: str) -> TranscriptionResult:
        """
        Transcribe audio from file, handling large files by chunking.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            TranscriptionResult instance with combined transcription
        """
        if self.whisper_model is None:
            self.load_whisper_model(self.config.model_size)
        
        try:
            file_size = os.path.getsize(file_path)
            logger.info(f"Transcribing file: {file_path} (size: {file_size / 1024 / 1024:.1f} MB)")
            
            # Check if file needs chunking
            if file_size > MAX_WHISPER_FILE_SIZE:
                logger.info(f"File exceeds {MAX_WHISPER_FILE_SIZE / 1024 / 1024:.0f} MB limit, using chunked transcription")
                chunks = self.split_audio_file(file_path)
                logger.info(f"Created {len(chunks)} chunks")
                
                all_texts = []
                all_confidences = []
                total_duration = 0
                
                for i, chunk_path in enumerate(chunks):
                    logger.info(f"Processing chunk {i + 1}/{len(chunks)}: {chunk_path}")
                    chunk_size = os.path.getsize(chunk_path) / 1024 / 1024
                    logger.info(f"Chunk size: {chunk_size:.1f} MB")
                    
                    result = self.whisper_model.transcribe(
                        chunk_path,
                        language=self.config.language,
                        fp16=False  # Use FP32 for CPU compatibility
                    )
                    
                    text = result['text'].strip() if result.get('text') else ''
                    logger.info(f"Chunk {i + 1} raw text length: {len(text)} chars")
                    logger.info(f"Chunk {i + 1} transcription: '{text[:100]}'{'...' if len(text) > 100 else ''}")
                    
                    if text:
                        all_texts.append(text)
                    else:
                        logger.warning(f"Chunk {i + 1} returned empty transcription")
                    
                    # Calculate confidence for this chunk
                    if 'segments' in result and result['segments']:
                        confidences = [seg.get('avg_logprob', 0.0) for seg in result['segments']]
                        confidence = np.mean([np.exp(c) for c in confidences]) if confidences else 0.0
                        all_confidences.append(confidence)
                        logger.info(f"Chunk {i + 1} confidence: {confidence:.4f}")
                    
                    # Get chunk duration
                    chunk_duration = result.get('duration', 0.0)
                    total_duration += chunk_duration
                    logger.info(f"Chunk {i + 1} duration: {chunk_duration:.2f}s")
                
                # Combine transcriptions with space
                combined_text = " ".join(all_texts)
                average_confidence = np.mean(all_confidences) if all_confidences else 0.0
                
                logger.info(f"Total transcribed text length: {len(combined_text)} chars")
                logger.info(f"Combined transcription: '{combined_text[:200]}'{'...' if len(combined_text) > 200 else ''}")
                logger.info(f"Average confidence: {average_confidence:.4f}")
                logger.info(f"Total duration: {total_duration:.2f}s")
                
                # Clean up chunks
                try:
                    import shutil
                    shutil.rmtree("/tmp/audio_chunks")
                    logger.info("Cleaned up temporary chunk files")
                except Exception as e:
                    logger.warning(f"Failed to clean up chunks: {e}")
                
                if not combined_text.strip():
                    logger.error("No transcription text found in any chunk")
                    raise ValueError("No speech detected in audio file")
                
                return TranscriptionResult(
                    text=combined_text,
                    language=self.config.language,
                    confidence=average_confidence,
                    duration=total_duration
                )
            else:
                # File is small enough, process directly
                logger.info(f"File size {file_size / 1024 / 1024:.1f} MB is within limits, processing directly")
                return self.transcribe_audio_from_file(file_path)
                
        except ValueError as e:
            logger.error(f"Transcription validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in chunked transcription: {e}", exc_info=True)
            raise